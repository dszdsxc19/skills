#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const os = require('os');
const { execFileSync } = require('child_process');
const { mkdir, writeFile, rename } = require('fs/promises');
const { postmanToBruno } = require('@usebruno/converters');
const {
  parseRequest,
  stringifyCollection,
  stringifyFolder,
  stringifyRequest
} = require('@usebruno/filestore');

function parseArgs(argv) {
  const options = {
    output: path.join(os.homedir(), 'Desktop', 'API', 'Postman Migrated'),
    openBruno: true
  };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--output') {
      options.output = path.resolve(argv[++i]);
    } else if (argv[i] === '--no-open') {
      options.openBruno = false;
    } else if (argv[i] === '--help' || argv[i] === '-h') {
      console.log('Usage: migrate.js [--output PATH] [--no-open]');
      process.exit(0);
    } else {
      throw new Error(`Unknown argument: ${argv[i]}`);
    }
  }
  return options;
}

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function fetchRetry(url, opts = {}, tries = 5) {
  let lastError;
  for (let i = 0; i < tries; i++) {
    try {
      const res = await fetch(url, opts);
      if (!res.ok) {
        throw new Error(`${res.status} ${res.statusText}: ${(await res.text()).slice(0, 300)}`);
      }
      return res;
    } catch (err) {
      lastError = err;
      await sleep(1000 * (i + 1));
    }
  }
  throw lastError;
}

async function getPostmanTargets() {
  const portFile = path.join(process.env.HOME, 'Library/Application Support/Postman/DevToolsActivePort');
  const readTargets = async () => {
    if (!fs.existsSync(portFile)) return null;
    const port = fs.readFileSync(portFile, 'utf8').split(/\n/)[0];
    try {
      const response = await fetch(`http://127.0.0.1:${port}/json/list`);
      if (!response.ok) return null;
      return await response.json();
    } catch {
      return null;
    }
  };

  let targets = await readTargets();
  if (targets?.some((target) => target.type === 'page')) return targets;

  execFileSync('open', ['-a', 'Postman'], { stdio: 'ignore' });
  for (let attempt = 0; attempt < 30; attempt++) {
    await sleep(1000);
    targets = await readTargets();
    if (targets?.some((target) => target.type === 'page')) return targets;
  }
  throw new Error('Postman did not expose a page target after 30 seconds.');
}

async function getPostmanAuth() {
  const targets = await getPostmanTargets();
  const page = targets.find((target) => target.type === 'page');
  if (!page) {
    throw new Error('Postman page target not found. Open Postman and try again.');
  }

  const ws = new WebSocket(page.webSocketDebuggerUrl);
  let id = 0;
  const pending = new Map();
  ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    if (message.id && pending.has(message.id)) {
      pending.get(message.id)(message);
      pending.delete(message.id);
    }
  };
  await new Promise((resolve) => {
    ws.onopen = resolve;
  });

  const send = (method, params = {}) =>
    new Promise((resolve) => {
      const messageId = ++id;
      pending.set(messageId, resolve);
      ws.send(JSON.stringify({ id: messageId, method, params }));
    });

  await send('Runtime.enable');
  const expression = `
    (async () => {
      const db = await new Promise((resolve, reject) => {
        const req = indexedDB.open('postman-app');
        req.onerror = () => reject(req.error);
        req.onsuccess = () => resolve(req.result);
      });
      const tx = db.transaction(['users', 'workspace_sessions'], 'readonly');
      const user = await new Promise((resolve) => {
        const req = tx.objectStore('users').get('currentUser');
        req.onsuccess = () => resolve(req.result);
        req.onerror = () => resolve(null);
      });
      const sessions = await new Promise((resolve) => {
        const req = tx.objectStore('workspace_sessions').getAll();
        req.onsuccess = () => resolve(req.result);
        req.onerror = () => resolve([]);
      });
      db.close();
      return {
        token: user.auth.access_token,
        userId: user.id,
        workspace: sessions[0]?.workspace
      };
    })()
  `;
  const result = await send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true });
  ws.close();
  const auth = result.result.result.value;
  const pageUrl = new URL(page.url);
  auth.appVersion = pageUrl.searchParams.get('desktopVersion') || '12.14.2';
  if (!auth.token || !auth.workspace) {
    throw new Error('Postman login token or active workspace was not found.');
  }
  return auth;
}

function safeName(name) {
  return String(name || 'Untitled')
    .replace(/[\\/:*?"<>|]+/g, '-')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, 120) || 'Untitled';
}

function safeFileName(name, fallback = 'Untitled') {
  return safeName(name || fallback)
    .replace(/^\.+$/, fallback)
    .replace(/^\./, '')
    .slice(0, 80);
}

async function writeUniqueFile(dir, baseName, ext, content, usedNames) {
  let name = safeFileName(baseName);
  let fileName = `${name}${ext}`;
  let counter = 2;
  while (usedNames.has(fileName.toLowerCase())) {
    fileName = `${name} ${counter}${ext}`;
    counter += 1;
  }
  usedNames.add(fileName.toLowerCase());
  await writeFile(path.join(dir, fileName), content);
}

async function writeBrunoItems(dir, items = []) {
  await mkdir(dir, { recursive: true });
  const usedNames = new Set(['bruno.json', 'collection.bru', 'folder.bru']);

  for (const item of items) {
    if (item.type === 'folder') {
      const folderName = safeFileName(item.name, 'Folder');
      let folderDir = path.join(dir, folderName);
      let counter = 2;
      while (fs.existsSync(folderDir)) {
        folderDir = path.join(dir, `${folderName} ${counter}`);
        counter += 1;
      }
      await mkdir(folderDir, { recursive: true });
      await writeFile(path.join(folderDir, 'folder.bru'), stringifyFolder(item, { format: 'bru' }));
      await writeBrunoItems(folderDir, item.items || []);
      continue;
    }

    await writeUniqueFile(
      dir,
      item.name || 'Request',
      '.bru',
      stringifyRequest(item, { format: 'bru' }),
      usedNames
    );
  }
}

function walkRequestFiles(dir, files = []) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (entry.name !== '_postman-json-backup') walkRequestFiles(fullPath, files);
    } else if (
      entry.name.endsWith('.bru') &&
      entry.name !== 'collection.bru' &&
      entry.name !== 'folder.bru'
    ) {
      files.push(fullPath);
    }
  }
  return files;
}

function updateBrunoPreferences(collectionPaths) {
  const preferenceFiles = [
    path.join(os.homedir(), 'Library/Application Support/Bruno/preferences.json'),
    path.join(os.homedir(), 'Library/Application Support/bruno/preferences.json')
  ];
  for (const preferenceFile of preferenceFiles) {
    if (!fs.existsSync(preferenceFile)) continue;
    const data = JSON.parse(fs.readFileSync(preferenceFile, 'utf8'));
    const existing = Array.isArray(data.lastOpenedCollections)
      ? data.lastOpenedCollections.filter((item) => !collectionPaths.includes(item))
      : [];
    data.lastOpenedCollections = [...collectionPaths, ...existing];
    fs.writeFileSync(preferenceFile, JSON.stringify(data, null, '\t'));
  }
}

function reopenBruno() {
  try {
    execFileSync('osascript', ['-e', 'tell application "Bruno" to quit'], { stdio: 'ignore' });
  } catch {}
  execFileSync('open', ['-a', 'Bruno'], { stdio: 'ignore' });
}

function varsToPostman(vars) {
  if (!Array.isArray(vars)) return [];
  return vars.map((v) => ({
    key: v.key || v.name,
    value: v.value ?? v.initialValue ?? '',
    type: v.type || 'default',
    disabled: v.enabled === false
  })).filter((v) => v.key);
}

function eventsToPostman(request) {
  const events = [];
  if (request.preRequestScript) {
    events.push({
      listen: 'prerequest',
      script: { type: 'text/javascript', exec: String(request.preRequestScript).split(/\r?\n/) }
    });
  }
  if (request.tests) {
    events.push({
      listen: 'test',
      script: { type: 'text/javascript', exec: String(request.tests).split(/\r?\n/) }
    });
  }
  return events.length ? events : undefined;
}

function bodyToPostman(request) {
  if (!request.dataMode || request.dataMode === 'params') return undefined;
  if (request.dataMode === 'raw') {
    return {
      mode: 'raw',
      raw: request.rawModeData || request.data || '',
      options: request.dataOptions || undefined
    };
  }
  if (request.dataMode === 'urlencoded') {
    return {
      mode: 'urlencoded',
      urlencoded: Array.isArray(request.data) ? request.data : []
    };
  }
  if (request.dataMode === 'formdata') {
    return {
      mode: 'formdata',
      formdata: Array.isArray(request.data) ? request.data : []
    };
  }
  return undefined;
}

function requestToPostman(request) {
  const item = {
    name: request.name || 'Untitled Request',
    request: {
      method: request.method || 'GET',
      header: Array.isArray(request.headerData)
        ? request.headerData.map((h) => ({
            key: h.key,
            value: h.value,
            disabled: h.enabled === false,
            description: h.description
          })).filter((h) => h.key)
        : [],
      url: request.url || ''
    }
  };

  const body = bodyToPostman(request);
  if (body) item.request.body = body;
  if (request.description) item.request.description = request.description;
  if (request.auth) item.request.auth = request.auth;
  const events = eventsToPostman(request);
  if (events) item.event = events;
  return item;
}

function collectionToPostman(collection) {
  const requestsById = new Map((collection.requests || []).map((request) => [request.id, request]));
  const foldersById = new Map((collection.folders || []).map((folder) => [folder.id, folder]));

  const buildFolder = (folder) => {
    const items = [];
    for (const childFolderId of folder.folders_order || []) {
      const child = foldersById.get(childFolderId);
      if (child) items.push(buildFolder(child));
    }
    for (const requestId of folder.order || []) {
      const request = requestsById.get(requestId);
      if (request) items.push(requestToPostman(request));
    }
    return {
      name: folder.name || 'Untitled Folder',
      item: items,
      description: folder.description || undefined
    };
  };

  const rootItems = [];
  for (const folderId of collection.folders_order || []) {
    const folder = foldersById.get(folderId);
    if (folder) rootItems.push(buildFolder(folder));
  }
  for (const requestId of collection.order || []) {
    const request = requestsById.get(requestId);
    if (request) rootItems.push(requestToPostman(request));
  }

  return {
    info: {
      _postman_id: collection.id,
      name: collection.name || 'Untitled Collection',
      schema: 'https://schema.getpostman.com/json/collection/v2.1.0/collection.json'
    },
    item: rootItems,
    variable: varsToPostman(collection.variables || collection.initialVariables),
    auth: collection.auth || undefined,
    event: collection.events || undefined
  };
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  const outDir = options.output;
  const rawDir = path.join(outDir, '_postman-json-backup');
  const auth = await getPostmanAuth();
  const headers = {
    'x-access-token': auth.token,
    'x-app-version': auth.appVersion,
    'x-entity-team-id': '0',
    accept: 'application/json'
  };

  let backupDir = null;
  if (fs.existsSync(outDir)) {
    const stamp = new Date().toISOString().replace(/[:.]/g, '-');
    backupDir = `${outDir}.backup-${stamp}`;
    await rename(outDir, backupDir);
  }
  await mkdir(rawDir, { recursive: true });

  const listUrl = `https://bifrost-https-v4.gw.postman.com/list/collection?workspace=${auth.workspace}&log=collectionSidebar`;
  const list = await (await fetchRetry(listUrl, { method: 'POST', headers })).json();
  const collections = list.data || [];
  const summary = [];

  for (const collectionSummary of collections) {
    const syncUrl = `https://bifrost-https-v4.gw.postman.com/collection/${collectionSummary.id}/sync?since_id=0&favorite=true`;
    const sync = await (await fetchRetry(syncUrl, { headers })).json();
    const entity = (sync.entities || []).find((item) => item.meta?.model === 'collection') || sync.entities?.[0];
    if (!entity?.data) continue;

    const postmanCollection = collectionToPostman(entity.data);
    const dirName = safeName(postmanCollection.info.name);
    const collectionDir = path.join(outDir, dirName);
    await mkdir(collectionDir, { recursive: true });

    await writeFile(
      path.join(rawDir, `${dirName}.postman_collection.json`),
      JSON.stringify(postmanCollection, null, 2)
    );

    const brunoCollection = await postmanToBruno(postmanCollection);
    const brunoConfig = {
      version: '1',
      name: brunoCollection.name,
      type: 'collection',
      ignore: ['node_modules', '.git']
    };

    await writeFile(path.join(collectionDir, 'bruno.json'), JSON.stringify(brunoConfig, null, 2));
    await writeFile(
      path.join(collectionDir, 'collection.bru'),
      stringifyCollection(brunoCollection.root, brunoConfig, { format: 'bru' })
    );
    await writeBrunoItems(collectionDir, brunoCollection.items || []);

    summary.push({
      name: postmanCollection.info.name,
      requests: entity.data.requests?.length || 0,
      folders: entity.data.folders?.length || 0,
      path: collectionDir
    });
  }

  const requestFiles = walkRequestFiles(outDir);
  for (const requestFile of requestFiles) {
    parseRequest(fs.readFileSync(requestFile, 'utf8'), { format: 'bru' });
  }
  const expectedRequests = summary.reduce((total, collection) => total + collection.requests, 0);
  if (requestFiles.length !== expectedRequests) {
    throw new Error(`Validation failed: expected ${expectedRequests} requests, generated ${requestFiles.length}.`);
  }

  await writeFile(path.join(outDir, 'migration-summary.json'), JSON.stringify(summary, null, 2));
  updateBrunoPreferences(summary.map((collection) => collection.path));
  if (options.openBruno) reopenBruno();

  console.log(JSON.stringify({
    outDir,
    backupDir,
    collectionCount: summary.length,
    requestCount: requestFiles.length,
    collections: summary
  }, null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
