(function () {
  function init() {
    var textarea = document.getElementById("id_content");
    if (!textarea || textarea.dataset.easymdeReady === "1") return;
    if (typeof EasyMDE === "undefined") return;

    textarea.dataset.easymdeReady = "1";

    var editor = new EasyMDE({
      element: textarea,
      autoDownloadFontAwesome: true,
      spellChecker: false,
      autosave: { enabled: false },
      minHeight: "420px",
      status: ["lines", "words", "cursor"],
      previewClass: ["editor-preview", "prose-minimal"],
      toolbar: [
        "bold", "italic", "strikethrough", "heading", "|",
        "code", "quote", "unordered-list", "ordered-list", "|",
        "link", "image", "table", "horizontal-rule", "|",
        "preview", "side-by-side", "fullscreen", "|",
        {
          name: "upload",
          action: function (editor) {
            openUploader(editor);
          },
          className: "fa fa-upload",
          title: "Upload image",
        },
        {
          name: "sticker",
          action: function (editor) {
            openStickerPicker(editor);
          },
          className: "fa fa-smile-o",
          title: "Insert sticker",
        },
        "|", "guide",
      ],
      renderingConfig: {
        codeSyntaxHighlighting: false,
      },
    });

    window.__postEditor = editor;
  }

  function getCookie(name) {
    var m = document.cookie.match("(^|;)\\s*" + name + "\\s*=\\s*([^;]+)");
    return m ? decodeURIComponent(m[2]) : "";
  }

  function openUploader(editor) {
    var input = document.createElement("input");
    input.type = "file";
    input.accept = "image/*";
    input.onchange = function () {
      var file = input.files[0];
      if (!file) return;
      var form = new FormData();
      form.append("file", file);
      form.append("kind", "image");
      fetch("/studio/upload/", {
        method: "POST",
        headers: { "X-CSRFToken": getCookie("csrftoken") },
        body: form,
        credentials: "same-origin",
      })
        .then(function (r) { return r.json(); })
        .then(function (data) {
          if (data && data.markdown) {
            var cm = editor.codemirror;
            cm.replaceSelection("\n" + data.markdown + "\n");
          } else {
            alert("Upload failed");
          }
        })
        .catch(function () { alert("Upload failed"); });
    };
    input.click();
  }

  function openStickerPicker(editor) {
    fetch("/studio/stickers/", { credentials: "same-origin" })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        var items = (data && data.items) || [];
        if (!items.length) {
          alert("No stickers yet. Upload some in the admin (MediaAssets → kind: sticker).");
          return;
        }
        var overlay = document.createElement("div");
        overlay.style.cssText = "position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:9999;display:flex;align-items:center;justify-content:center;";
        var panel = document.createElement("div");
        panel.style.cssText = "background:#fff;padding:16px;border-radius:8px;max-width:560px;width:90%;max-height:70vh;overflow:auto;";
        panel.innerHTML = "<h3 style=\"margin:0 0 12px;\">Stickers</h3>";
        var grid = document.createElement("div");
        grid.style.cssText = "display:grid;grid-template-columns:repeat(4,1fr);gap:8px;";
        items.forEach(function (it) {
          var btn = document.createElement("button");
          btn.type = "button";
          btn.style.cssText = "border:1px solid #ddd;padding:4px;background:#fff;cursor:pointer;";
          btn.innerHTML = '<img src="' + it.url + '" style="width:100%;height:80px;object-fit:contain;" />';
          btn.onclick = function () {
            editor.codemirror.replaceSelection(it.markdown);
            document.body.removeChild(overlay);
          };
          grid.appendChild(btn);
        });
        panel.appendChild(grid);
        var close = document.createElement("button");
        close.type = "button";
        close.textContent = "Close";
        close.style.cssText = "margin-top:12px;padding:6px 12px;";
        close.onclick = function () { document.body.removeChild(overlay); };
        panel.appendChild(close);
        overlay.appendChild(panel);
        document.body.appendChild(overlay);
      });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
