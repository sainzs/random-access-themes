// Print CGWindowID of the frontmost normal window owned by <app name>.
import CoreGraphics
import Foundation
let target = CommandLine.arguments.dropFirst().first ?? ""
let opts: CGWindowListOption = [.optionOnScreenOnly, .excludeDesktopElements]
guard let list = CGWindowListCopyWindowInfo(opts, kCGNullWindowID) as? [[String: Any]] else { exit(1) }
for w in list {
    let owner = w[kCGWindowOwnerName as String] as? String ?? ""
    let layer = w[kCGWindowLayer as String] as? Int ?? -1
    let b = w[kCGWindowBounds as String] as? [String: Any] ?? [:]
    let h = (b["Height"] as? Double) ?? 0
    if owner.lowercased().contains(target.lowercased()) && layer == 0 && h > 100 {
        print(w[kCGWindowNumber as String] as? Int ?? 0); exit(0)
    }
}
exit(2)
