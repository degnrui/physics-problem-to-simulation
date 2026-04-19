// --------------------------------------------fonts--------------------------------------------

new FontFace("GB Pinyinok-B", `url('https://static-nginx-online.fbcontent.cn/metis-tinymce-plugins-static/pinyin/font/a2291f45943faa5fe3c71fc54dfee6cd.woff2')`).load().then(function (font) {
  document.fonts.add(font);
}).catch(function (error) {
  console.log("Failed to load pinyin font: " + error);
});

new FontFace("KaiTi", `url('https://static-nginx-online.fbcontent.cn/metis-tinymce-plugins-static/pinyin/font/kaiti.ttf')`).load().then(function (font) {
  document.fonts.add(font);
}).catch(function (error) {
  console.log("Failed to load KaiTi font: " + error);
});

// --------------------------------------------scripts--------------------------------------------

const scripts = [
  'https://static-nginx-online.fbcontent.cn/metis-tinymce-plugins-static/web-components/shiny-blanks/js/index.js',
  'https://static-nginx-online.fbcontent.cn/metis-tinymce-plugins-static/web-components/full-line-blank/js/index.js'
]

scripts.forEach(function (src) {
  const script = document.createElement('script');
  script.src = src;
  document.head.appendChild(script);
});
