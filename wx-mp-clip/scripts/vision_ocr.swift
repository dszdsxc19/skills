import Vision
import AppKit

// 保留文字位置和置信度，使上层能按版面恢复段落，并追溯每一处识别结果。
struct TextLine: Codable {
    let text: String
    let x: Double
    let y: Double
    let width: Double
    let height: Double
    let confidence: Float
}
struct PageResult: Codable {
    let file: String
    let lines: [TextLine]
    let error: String?
}
let arguments = Array(CommandLine.arguments.dropFirst())
let correction = !arguments.contains("--no-correction")
var pages: [PageResult] = []
for path in arguments.filter({ $0 != "--no-correction" }) {
    let file = (path as NSString).lastPathComponent
    do {
        guard let image = NSImage(contentsOfFile: path),
              let cg = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
            throw NSError(domain: "wx-mp-clip", code: 1, userInfo: [NSLocalizedDescriptionKey: "图片无法解码"])
        }
        let request = VNRecognizeTextRequest()
        request.recognitionLanguages = ["zh-Hans", "en-US"]
        request.recognitionLevel = .accurate
        request.usesLanguageCorrection = correction
        try VNImageRequestHandler(cgImage: cg, options: [:]).perform([request])
        let lines = (request.results ?? []).compactMap { observation -> TextLine? in
            guard let candidate = observation.topCandidates(1).first else { return nil }
            let box = observation.boundingBox
            return TextLine(text: candidate.string, x: box.minX, y: box.minY,
                            width: box.width, height: box.height, confidence: candidate.confidence)
        }
        pages.append(PageResult(file: file, lines: lines, error: nil))
    } catch {
        // 按页报告错误，调用方只重试失败页，原始图片及已有识别结果继续保留。
        pages.append(PageResult(file: file, lines: [], error: error.localizedDescription))
    }
}
let data = try JSONEncoder().encode(pages)
print(String(decoding: data, as: UTF8.self))
