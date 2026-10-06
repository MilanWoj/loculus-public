// Author: MilanWoj
import Cocoa
import WebKit

class AppDelegate: NSObject, NSApplicationDelegate, NSWindowDelegate {
    var window: NSWindow!
    var webView: WKWebView!
    var launchLog: FileHandle?

    func applicationDidFinishLaunching(_ notification: Notification) {
        openLaunchLog()
        runStartScript()
        buildWindow()
        pollBackendHealth()
    }

    func projectRoot() -> String {
        if let path = Bundle.main.path(forResource: "project_root", ofType: "txt"),
           let content = try? String(contentsOfFile: path, encoding: .utf8) {
            return content.trimmingCharacters(in: .whitespacesAndNewlines)
        }
        return NSHomeDirectory() + "/Projects/loculus"
    }

    func openLaunchLog() {
        let path = projectRoot() + "/app-launch.log"
        FileManager.default.createFile(atPath: path, contents: nil)
        launchLog = FileHandle(forWritingAtPath: path)
    }

    func log(_ message: String) {
        guard let data = (message + "\n").data(using: .utf8) else { return }
        launchLog?.write(data)
    }

    func runStartScript() {
        let task = Process()
        task.executableURL = URL(fileURLWithPath: "/bin/bash")
        task.arguments = [projectRoot() + "/scripts/start-prod.sh"]
        task.currentDirectoryURL = URL(fileURLWithPath: projectRoot())

        let pipe = Pipe()
        task.standardOutput = pipe
        task.standardError = pipe
        pipe.fileHandleForReading.readabilityHandler = { [weak self] handle in
            let data = handle.availableData
            if !data.isEmpty, let text = String(data: data, encoding: .utf8) {
                self?.log(text)
            }
        }

        do {
            try task.run()
        } catch {
            log("failed to launch start-prod.sh: \(error)")
        }
    }

    func buildWindow() {
        window = NSWindow(
            contentRect: NSRect(x: 0, y: 0, width: 1100, height: 760),
            styleMask: [.titled, .closable, .miniaturizable, .resizable],
            backing: .buffered,
            defer: false
        )
        window.title = "Loculus"
        window.center()
        window.delegate = self

        webView = WKWebView(frame: window.contentView!.bounds)
        webView.autoresizingMask = [.width, .height]
        window.contentView?.addSubview(webView)

        window.makeKeyAndOrderFront(nil)
        NSApp.activate(ignoringOtherApps: true)
    }

    func pollBackendHealth() {
        let url = URL(string: "http://127.0.0.1:8000/api/health")!
        var attempts = 0

        func check() {
            attempts += 1
            let task = URLSession.shared.dataTask(with: url) { [weak self] data, response, error in
                DispatchQueue.main.async {
                    if let http = response as? HTTPURLResponse, http.statusCode == 200 {
                        self?.loadApp()
                    } else if attempts < 60 {
                        DispatchQueue.main.asyncAfter(deadline: .now() + 1) { check() }
                    } else {
                        self?.log("backend did not become healthy after 60s")
                    }
                }
            }
            task.resume()
        }
        check()
    }

    func loadApp() {
        webView.load(URLRequest(url: URL(string: "http://127.0.0.1:8000")!))
    }

    func windowWillClose(_ notification: Notification) {
        stopStackAndTerminate()
    }

    func stopStackAndTerminate() {
        let task = Process()
        task.executableURL = URL(fileURLWithPath: "/bin/bash")
        task.arguments = [projectRoot() + "/scripts/stop.sh"]
        task.currentDirectoryURL = URL(fileURLWithPath: projectRoot())
        try? task.run()
        task.waitUntilExit()
        NSApp.terminate(nil)
    }
}
