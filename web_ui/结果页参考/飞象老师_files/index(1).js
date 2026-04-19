"use strict";

function _typeof(o) { "@babel/helpers - typeof"; return _typeof = "function" == typeof Symbol && "symbol" == typeof Symbol.iterator ? function (o) { return typeof o; } : function (o) { return o && "function" == typeof Symbol && o.constructor === Symbol && o !== Symbol.prototype ? "symbol" : typeof o; }, _typeof(o); }
function _classCallCheck(a, n) { if (!(a instanceof n)) throw new TypeError("Cannot call a class as a function"); }
function _defineProperties(e, r) { for (var t = 0; t < r.length; t++) { var o = r[t]; o.enumerable = o.enumerable || !1, o.configurable = !0, "value" in o && (o.writable = !0), Object.defineProperty(e, _toPropertyKey(o.key), o); } }
function _createClass(e, r, t) { return r && _defineProperties(e.prototype, r), t && _defineProperties(e, t), Object.defineProperty(e, "prototype", { writable: !1 }), e; }
function _callSuper(t, o, e) { return o = _getPrototypeOf(o), _possibleConstructorReturn(t, _isNativeReflectConstruct() ? Reflect.construct(o, e || [], _getPrototypeOf(t).constructor) : o.apply(t, e)); }
function _possibleConstructorReturn(t, e) { if (e && ("object" == _typeof(e) || "function" == typeof e)) return e; if (void 0 !== e) throw new TypeError("Derived constructors may only return object or undefined"); return _assertThisInitialized(t); }
function _assertThisInitialized(e) { if (void 0 === e) throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); return e; }
function _inherits(t, e) { if ("function" != typeof e && null !== e) throw new TypeError("Super expression must either be null or a function"); t.prototype = Object.create(e && e.prototype, { constructor: { value: t, writable: !0, configurable: !0 } }), Object.defineProperty(t, "prototype", { writable: !1 }), e && _setPrototypeOf(t, e); }
function _wrapNativeSuper(t) { var r = "function" == typeof Map ? new Map() : void 0; return _wrapNativeSuper = function _wrapNativeSuper(t) { if (null === t || !_isNativeFunction(t)) return t; if ("function" != typeof t) throw new TypeError("Super expression must either be null or a function"); if (void 0 !== r) { if (r.has(t)) return r.get(t); r.set(t, Wrapper); } function Wrapper() { return _construct(t, arguments, _getPrototypeOf(this).constructor); } return Wrapper.prototype = Object.create(t.prototype, { constructor: { value: Wrapper, enumerable: !1, writable: !0, configurable: !0 } }), _setPrototypeOf(Wrapper, t); }, _wrapNativeSuper(t); }
function _construct(t, e, r) { if (_isNativeReflectConstruct()) return Reflect.construct.apply(null, arguments); var o = [null]; o.push.apply(o, e); var p = new (t.bind.apply(t, o))(); return r && _setPrototypeOf(p, r.prototype), p; }
function _isNativeReflectConstruct() { try { var t = !Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function () {})); } catch (t) {} return (_isNativeReflectConstruct = function _isNativeReflectConstruct() { return !!t; })(); }
function _isNativeFunction(t) { try { return -1 !== Function.toString.call(t).indexOf("[native code]"); } catch (n) { return "function" == typeof t; } }
function _setPrototypeOf(t, e) { return _setPrototypeOf = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function (t, e) { return t.__proto__ = e, t; }, _setPrototypeOf(t, e); }
function _getPrototypeOf(t) { return _getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function (t) { return t.__proto__ || Object.getPrototypeOf(t); }, _getPrototypeOf(t); }
function _defineProperty(e, r, t) { return (r = _toPropertyKey(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: !0, configurable: !0, writable: !0 }) : e[r] = t, e; }
function _toPropertyKey(t) { var i = _toPrimitive(t, "string"); return "symbol" == _typeof(i) ? i : i + ""; }
function _toPrimitive(t, r) { if ("object" != _typeof(t) || !t) return t; var e = t[Symbol.toPrimitive]; if (void 0 !== e) { var i = e.call(t, r || "default"); if ("object" != _typeof(i)) return i; throw new TypeError("@@toPrimitive must return a primitive value."); } return ("string" === r ? String : Number)(t); }
if (!document.fonts.check('12px GB Pinyinok-B')) {
  var host = "https://static-nginx-online.fbcontent.cn/metis-tinymce-plugins-static";
  new FontFace("GB Pinyinok-B", "url('".concat(host, "/pinyin/font/a2291f45943faa5fe3c71fc54dfee6cd.woff2')")).load().then(function (font) {
    document.fonts.add(font);
  })["catch"](function (error) {
    console.log("Failed to load pinyin font: " + error);
  });
}
if (!document.fonts.check('12px KaiTi')) {
  var _host = "https://static-nginx-online.fbcontent.cn/metis-tinymce-plugins-static";
  new FontFace("KaiTi", "url('".concat(_host, "/pinyin/font/kaiti.ttf')")).load().then(function (font) {
    document.fonts.add(font);
  })["catch"](function (error) {
    console.log("Failed to load KaiTi font: " + error);
  });
}
(function () {
  var ShinyBlank = /*#__PURE__*/function (_HTMLElement) {
    function ShinyBlank() {
      var _this;
      _classCallCheck(this, ShinyBlank);
      _this = _callSuper(this, ShinyBlank);
      _defineProperty(_this, "group", null);
      _this.render();
      return _this;
    }
    _inherits(ShinyBlank, _HTMLElement);
    return _createClass(ShinyBlank, [{
      key: "attributeChangedCallback",
      value: function attributeChangedCallback() {
        this.updateGroupByDataInfo();
      }
    }, {
      key: "getStyle",
      value: function getStyle() {
        var _JSON$parse;
        var style = document.createElement('style');
        var customStyle = JSON.parse(this.getAttribute("data-style")) || {};
        var size = (customStyle === null || customStyle === void 0 ? void 0 : customStyle.size) || 56; // 田字格的大小，默认56 * 56
        var fontSize = (customStyle === null || customStyle === void 0 ? void 0 : customStyle.fontSize) || 36; // 田字格中字体大小，默认36
        var rtFontSize = (customStyle === null || customStyle === void 0 ? void 0 : customStyle.rtFontSize) || 14; // 拼音字体大小，默认14
        var height = (customStyle === null || customStyle === void 0 ? void 0 : customStyle.height) || 75; // 容器整体高度，默认75
        var backgroundColor = (customStyle === null || customStyle === void 0 ? void 0 : customStyle.backgroundColor) || ''; // 田字格背景颜色
        var fontFamily = (customStyle === null || customStyle === void 0 ? void 0 : customStyle.fontFamily) || ''; // 田字格展示中文时的字体

        style.textContent = "\n\n    rt {\n      font-size:".concat(rtFontSize, "px;\n      font-family: \"GB Pinyinok-B\" !important;\n      white-space: nowrap;\n    }\n\n    .wrapper{\n      vertical-align:middle;\n      position: relative;\n      width: ").concat(size, "px;\n      height: ").concat(height, "px;\n      display: inline-block;\n    }\n    .wrapper:not(:first-child) {\n       margin-left: -1px;\n    }\n\n    .hanzi {\n      width: ").concat(size, "px;\n      height: ").concat(size, "px;\n      display: inline-block;\n      background-size: cover;\n      text-align: center;\n      line-height: ").concat(size, "px;\n      font-size: ").concat(fontSize, "px;\n      font-family: ").concat(fontFamily ? "\"".concat(fontFamily, "\"") : 'KaiTi,Kai,FZKai-Z03,STKaiti, KaiTi_GB2312, DFKai-SB', ";\n      vertical-align: text-top;\n      ").concat(backgroundColor ? "background-color: ".concat(backgroundColor) : '', "\n      ").concat(this.getAttribute('with-border') === 'true' ? "\n      position: relative;\n    }\n    .hanzi:empty::after {\n      content: '';\n      position: absolute;\n      top: 0;\n      bottom: 0;\n      left: 2px;\n      right: 2px;\n      background: green;\n      z-index: 9999;\n    " : '', "\n    }\n\n    ").concat(this.getAttribute('with-border') === 'true' && ((_JSON$parse = JSON.parse(this.getAttribute("data-info"))) === null || _JSON$parse === void 0 ? void 0 : _JSON$parse.showHanzi) === false ? "\n    .hanzi {\n      position: relative;\n    }\n    .hanzi::after {\n      content: '';\n      position: absolute;\n      top: 0;\n      bottom: 0;\n      left: 2px;\n      right: 2px;\n      background: green;\n      z-index: 9999;\n    }\n    " : '', "\n\n    .tianzi{\n      background-image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iODBweCIgaGVpZ2h0PSI4MHB4IiB2ZXJzaW9uPSIxLjEiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0tMiA0MCBMODAgNDAiIHN0cm9rZS1kYXNoYXJyYXk9IjQsNCIgc3Ryb2tlLXdpZHRoPSIxIiBzdHJva2U9IiM2NjYiIGZpbGwtb3BhY2l0eT0iMCIvPgo8cGF0aCBkPSJNNDAgLTIgTDQwIDgwIiBzdHJva2UtZGFzaGFycmF5PSI0LDQiIHN0cm9rZS13aWR0aD0iMSIgc3Ryb2tlPSIjNjY2IiBmaWxsLW9wYWNpdHk9IjAiLz4KPHBhdGggZD0iTTEgMSBsNzggMCBsMCA3OCBsLTc4IDAgWiIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2U9IiMxMTEiIGZpbGwtb3BhY2l0eT0iMCIvPgo8L3N2Zz4=);\n    }\n    .mizi{\n      background-image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI4MCIgaGVpZ2h0PSI4MCIgdmlld0JveD0iMCAwIDU2LjQyNCA1Ni40MjQiPjxwYXRoIGQ9Ik0uMjEyLjIxMmg1NnY1NmgtNTZ2LTU2em0xLjUgMS41djUzaDUzdi01M2gtNTN6IiBmaWxsPSIjMTgyMTI5Ii8+PHBhdGggZD0iTTEuOTYyIDI4LjUxMmEuMy4zIDAgMCAxIDAtLjZoLjgwMnYuNmgtLjgwMnptMi4xNTIgMGgxLjU2di0uNmgtMS41NnYuNnptMi45MzEgMGgxLjU0MnYtLjZINy4wNDV2LjZ6bTIuOTIgMGgxLjQ3NHYtLjZIOS45NjZ2LjZ6bTIuODU2IDBoMS42Mjh2LS42aC0xLjYyOHYuNnptMi45NDIgMGgxLjU0N3YtLjZoLTEuNTQ3di42em0yLjkzNSAwaDEuNjIxdi0uNkgxOC43di42em0yLjg1NyAwaDEuNjY5di0uNmgtMS42N3YuNnptMi45MzMgMGgxLjQ4NnYtLjZoLTEuNDg2di42em0yLjk3NyAwaDEuNDk0di0uNmgtMS40OTR2LjZ6bTIuOTg1IDBoMS40ODZ2LS42SDMwLjQ1di42em0yLjc1IDBoMS42N3YtLjZIMzMuMnYuNnptMi45MDUgMGgxLjYydi0uNmgtMS42MnYuNnptMy4wMDkgMGgxLjU0N3YtLjZoLTEuNTQ3di42em0yLjg2IDBoMS42Mjl2LS42aC0xLjYyOHYuNnptMy4wMSAwaDEuNDc0di0uNmgtMS40NzN2LjZ6bTIuODUyIDBoMS41NDN2LS42aC0xLjU0M3YuNnptMi45MTMgMGgxLjU2MXYtLjZoLTEuNTZ2LjZ6bTMuNzEzIDBoLS44MDJ2LS42aC44MDJhLjMuMyAwIDEgMSAwIC42ek0yOC41MTIuOTg0Vi4yMTJoLS42di43NzJoLjZ6bS0uNiAxLjM5MnYxLjUzNWguNlYyLjM3NmgtLjZ6bTAgMi44ODF2MS42NjFoLjZ2LTEuNjZoLS42em0wIDMuMDI3djEuNjI3aC42VjguMjg0aC0uNnptMCAzLjAwNXYxLjQzOWguNnYtMS40MzloLS42em0wIDIuOTMydjEuNTQ0aC42VjE0LjIyaC0uNnptMCAyLjkzdjEuNjJoLjZ2LTEuNjJoLS42em0wIDIuODU2djEuNjczaC42di0xLjY3M2gtLjZ6bTAgMi45NDN2MS43MDhoLjZWMjIuOTVoLS42em0wIDIuOTk3djEuNTFoLjZ2LTEuNTFoLS42em0wIDMuMDJ2MS41MWguNnYtMS41MWgtLjZ6bTAgMi44djEuNzA4aC42di0xLjcwOGgtLjZ6bTAgMi45Nzd2MS42NzNoLjZ2LTEuNjczaC0uNnptMCAyLjkxdjEuNjJoLjZ2LTEuNjJoLS42em0wIDMuMDA2djEuNTQzaC42VjQwLjY2aC0uNnptMCAzLjAzN3YxLjQzOGguNnYtMS40MzhoLS42em0wIDIuODE2djEuNjI3aC42di0xLjYyN2gtLjZ6bTAgMi45OTN2MS42NjFoLjZ2LTEuNjZoLS42em0wIDMuMDA3djEuNTM1aC42di0xLjUzNWgtLjZ6bTAgMi45Mjd2Ljc3MmguNnYtLjc3MmgtLjZ6IiBmaWxsLXJ1bGU9ImV2ZW5vZGQiIGZpbGw9IiMxODIxMjkiLz48cGF0aCBkPSJNNTUuODM0IDEuMDE0bC41OS0uNTlMNTYgMGwtLjU5LjU5LjQyNC40MjR6bS0xLjQwOC41NmwtMS4xODIgMS4xODIuNDI0LjQyNCAxLjE4Mi0xLjE4Mi0uNDI0LS40MjR6bS0yLjEzIDIuMTNsLTEuMTYgMS4xNi40MjUuNDI0IDEuMTYtMS4xNi0uNDI0LS40MjV6bS0yLjE0IDIuMTRsLTEuMTYzIDEuMTYyLjQyNS40MjUgMS4xNjItMS4xNjItLjQyNS0uNDI1em0tMi4xNzQgMi4xNzRMNDYuOCA5LjJsLjQyNC40MjQgMS4xODMtMS4xODMtLjQyNC0uNDI0ek00NS44MSAxMC4xOWwtMS4xNTQgMS4xNTQuNDI0LjQyNCAxLjE1NC0xLjE1NC0uNDI0LS40MjR6bS0yLjIxNCAyLjIxNGwtMS4wOSAxLjA5LjQyNC40MjUgMS4wOS0xLjA5LS40MjQtLjQyNXptLTIuMDY4IDIuMDY4bC0xLjE0IDEuMTQuNDI0LjQyNCAxLjE0LTEuMTQtLjQyNC0uNDI0em0tMi4xNTggMi4xNTdsLTEuMTgyIDEuMTgzLjQyNC40MjQgMS4xODMtMS4xODItLjQyNS0uNDI1em0tMi4yMzIgMi4yMzNsLTEuMDY0IDEuMDY0LjQyNC40MjQgMS4wNjQtMS4wNjMtLjQyNC0uNDI1em0tMi4xMzkgMi4xMzlsLTEuMDg1IDEuMDg0LjQyNS40MjUgMS4wODUtMS4wODUtLjQyNS0uNDI0em0tMi4xNzggMi4xNzdsLTEuMSAxLjEuNDI1LjQyNSAxLjEtMS4xLS40MjUtLjQyNXptLTIuMDQ2IDIuMDQ3bC0xLjI2NyAxLjI2Ny40MjQuNDI0IDEuMjY3LTEuMjY2LS40MjQtLjQyNXptLTIuMjIgMi4yMmwtMS4xMTEgMS4xMS40MjQuNDI1IDEuMTEyLTEuMTExLS40MjQtLjQyNXptLTIuMDYzIDIuMDYzbC0xLjI2NyAxLjI2Ny40MjQuNDI0IDEuMjY3LTEuMjY3LS40MjQtLjQyNHptLTIuMjE0IDIuMjE0bC0xLjEgMS4xLjQyNC40MjQgMS4xLTEuMS0uNDI0LS40MjR6bS0yLjE5MyAyLjE5M0wyMSAzNWwuNDI0LjQyNCAxLjA4NS0xLjA4NS0uNDI0LS40MjR6bS0yLjE2IDIuMTZsLTEuMDYzIDEuMDYzLjQyNC40MjQgMS4wNjQtMS4wNjMtLjQyNS0uNDI1em0tMi4xMTMgMi4xMTNsLTEuMTgzIDEuMTgzLjQyNC40MjQgMS4xODMtMS4xODMtLjQyNC0uNDI0em0tMi4yIDIuMmwtMS4xNCAxLjE0LjQyMy40MjUgMS4xNDEtMS4xNC0uNDI0LS40MjV6bS0yLjExOCAyLjExOGwtMS4wOSAxLjA5LjQyNC40MjQgMS4wOS0xLjA5LS40MjQtLjQyNHptLTIuMTUgMi4xNWwtMS4xNTUgMS4xNTQuNDI1LjQyNSAxLjE1NC0xLjE1NC0uNDI1LS40MjV6TTkuMiA0Ni44bC0xLjE4NCAxLjE4My40MjUuNDI1IDEuMTgzLTEuMTgzLS40MjQtLjQyNXptLTIuMTk1IDIuMTk1bC0xLjE2MiAxLjE2Mi40MjQuNDI0IDEuMTYyLTEuMTYyLS40MjQtLjQyNHptLTIuMTQzIDIuMTQzbC0xLjE2IDEuMTYuNDI0LjQyNCAxLjE2LTEuMTYtLjQyNC0uNDI0em0tMi4xMDggMi4xMDdsLTEuMTgyIDEuMTgyLjQyNS40MjUgMS4xODItMS4xODItLjQyNS0uNDI1ek0uNTkgNTUuNDFMMCA1NmwuNDI0LjQyNC41OS0uNTktLjQyNC0uNDI0eiIgZmlsbC1ydWxlPSJldmVub2RkIiBmaWxsPSIjMTgyMTI5Ii8+PHBhdGggZD0iTTEuMDE0LjU5TC40MjQgMCAwIC40MjRsLjU5LjU5LjQyNC0uNDI0em0uNTYgMS40MDhMMi43NTUgMy4xOGwuNDI1LS40MjQtMS4xODItMS4xODItLjQyNC40MjR6bTIuMTI5IDIuMTNsMS4xNiAxLjE2LjQyNC0uNDI1LTEuMTYtMS4xNi0uNDI0LjQyNHptMi4xNDEgMi4xNGwxLjE2MiAxLjE2My40MjQtLjQyNS0xLjE2Mi0xLjE2Mi0uNDI0LjQyNXptMi4xNzMgMi4xNzRsMS4xODQgMS4xODMuNDI0LS40MjQtMS4xODMtMS4xODMtLjQyNS40MjR6bTIuMTcyIDIuMTcybDEuMTU0IDEuMTU0LjQyNS0uNDI0LTEuMTU0LTEuMTU0LS40MjUuNDI0em0yLjIxNSAyLjIxNGwxLjA5IDEuMDkuNDI1LS40MjMtMS4wOS0xLjA5LS40MjUuNDIzem0yLjA2NyAyLjA2OGwxLjE0IDEuMTQuNDI1LS40MjQtMS4xNC0xLjE0LS40MjUuNDI0em0yLjE1OCAyLjE1OGwxLjE4MyAxLjE4Mi40MjQtLjQyNC0xLjE4My0xLjE4My0uNDI0LjQyNXptMi4yMzMgMi4yMzNsMS4wNjMgMS4wNjMuNDI1LS40MjQtMS4wNjQtMS4wNjQtLjQyNC40MjV6TTIxIDIxLjQyNWwxLjA4NSAxLjA4NS40MjQtLjQyNS0xLjA4NC0xLjA4NC0uNDI1LjQyNHptMi4xNzggMi4xNzhsMS4xIDEuMS40MjQtLjQyNS0xLjEtMS4xLS40MjQuNDI1em0yLjA0NyAyLjA0N2wxLjI2NyAxLjI2Ni40MjQtLjQyNC0xLjI2Ny0xLjI2Ny0uNDI0LjQyNXptMi4yMTkgMi4yMTlsMS4xMTIgMS4xMTEuNDI0LS40MjQtMS4xMTItMS4xMTItLjQyNC40MjV6bTIuMDY0IDIuMDYzbDEuMjY3IDEuMjY3LjQyNC0uNDI0LTEuMjY3LTEuMjY3LS40MjQuNDI0em0yLjIxNCAyLjIxNGwxLjEgMS4xLjQyNC0uNDI0LTEuMS0xLjEtLjQyNC40MjR6bTIuMTkzIDIuMTkzbDEuMDg0IDEuMDg1LjQyNS0uNDI0LTEuMDg1LTEuMDg1LS40MjQuNDI0em0yLjE2IDIuMTZsMS4wNjMgMS4wNjMuNDI0LS40MjQtMS4wNjQtMS4wNjQtLjQyNC40MjV6bTIuMTEzIDIuMTEzbDEuMTgyIDEuMTgzLjQyNS0uNDI0LTEuMTgzLTEuMTgzLS40MjQuNDI0em0yLjIgMi4ybDEuMTQgMS4xNC40MjUtLjQyMy0xLjE0MS0xLjE0MS0uNDI0LjQyNHptMi4xMTcgMi4xMThsMS4wOSAxLjA5LjQyNS0uNDI0LTEuMDktMS4wOS0uNDI1LjQyNHptMi4xNTEgMi4xNWwxLjE1NCAxLjE1NS40MjQtLjQyNS0xLjE1NC0xLjE1NC0uNDI0LjQyNXptMi4xNDMgMi4xNDRsMS4xODMgMS4xODMuNDI0LS40MjUtMS4xODMtMS4xODMtLjQyNC40MjV6bTIuMTk0IDIuMTk0bDEuMTYyIDEuMTYyLjQyNS0uNDI0LTEuMTYyLTEuMTYyLS40MjUuNDI0em0yLjE0MyAyLjE0M2wxLjE2IDEuMTYuNDI1LS40MjQtMS4xNi0xLjE2LS40MjUuNDI0em0yLjEwOCAyLjEwOGwxLjE4MiAxLjE4Mi40MjQtLjQyNS0xLjE4Mi0xLjE4Mi0uNDI0LjQyNXptMi4xNjYgMi4xNjVsLjU5LjU5LjQyNC0uNDI0LS41OS0uNTktLjQyNC40MjR6IiBmaWxsLXJ1bGU9ImV2ZW5vZGQiIGZpbGw9IiMxODIxMjkiLz48L3N2Zz4=);\n    }\n\n    .emphasized-styling {\n      background-color: rgba(172, 255, 48, 0.5);\n    }\n\n    .metis-document-render__index-blank {\n      color: white;\n      transform: scale(0.001);\n      position: absolute;\n      white-space: nowrap;\n    }\n    .metis-document-render__index-blank-start {\n      left: 0;\n      top: 40%;\n      transform: translateY(-50%) scale(0.001);\n      transform-origin: center left;\n    }\n    .metis-document-render__index-blank-end {\n      left: 0;\n      top: 60%;\n      transform: translateY(-50%) scale(0.001);\n      transform-origin: center left;\n    }\n  }\n\n  ");
        return style;
      }
    }, {
      key: "updateGroupByDataInfo",
      value: function updateGroupByDataInfo() {
        var dataInfo = JSON.parse(this.getAttribute("data-info"));
        if (dataInfo) {
          this.group.innerHTML = '';
          var curIndex = 0;
          for (var i = 0; i < dataInfo.cells.length; i++) {
            var cell = dataInfo.cells[i];
            this.renderCell(cell, dataInfo, curIndex);
            if (!dataInfo.showHanzi || !cell.hanzi) {
              curIndex++;
            }
          }
        }
      }
    }, {
      key: "renderCell",
      value: function renderCell(cell, dataInfo) {
        var blankIndex = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : 0;
        var hanzi = cell.hanzi,
          pinyin = cell.pinyin;
        var showPinyin = dataInfo.showPinyin,
          showHanzi = dataInfo.showHanzi,
          adjoining = dataInfo.adjoining,
          type = dataInfo.type;
        var wrapper = document.createElement('span');
        wrapper.setAttribute('class', 'wrapper');
        var ruby = document.createElement('ruby');
        var hanziSpan = document.createElement('span');
        hanziSpan.setAttribute('class', "hanzi ".concat(type));

        // const rpLeft = document.createElement('rp');
        // rp.textContent = "("

        // const rpRight = document.createElement('rp');
        // rp.textContent = ")"

        var rt = document.createElement('rt');
        hanziSpan.innerHTML = showHanzi && hanzi ? hanzi : '';
        if (!showHanzi || !hanzi) {
          if (this.getAttribute('emphasized-styling')) {
            hanziSpan.classList.add('emphasized-styling');
          }
        }
        rt.innerHTML = showPinyin && pinyin ? pinyin : "&nbsp;";
        if (!adjoining) {
          wrapper.style.margin = '0 2px';
        }

        // 添加空索引
        var indexStart = parseInt(this.getAttribute('blank-start') || '0');
        var questionMark = this.getAttribute('question-mark') || '0-0';
        var blankMark = "".concat(questionMark, "-").concat(blankIndex + indexStart);
        if ((!showHanzi || !hanzi) && this.getAttribute('need-index') === 'true') {
          var blankSpan = document.createElement('span');
          blankSpan.setAttribute('class', 'metis-document-render__index-blank metis-document-render__index-blank-start');
          blankSpan.innerHTML = "&#9829;blank-id-start".concat(blankMark, "blank-id-end&#9829;&#8595;");
          wrapper.appendChild(blankSpan);
        }
        this.group.appendChild(wrapper);
        wrapper.appendChild(ruby);
        if ((!showHanzi || !hanzi) && this.getAttribute('need-index') === 'true') {
          var _blankSpan = document.createElement('span');
          _blankSpan.setAttribute('class', 'metis-document-render__index-blank metis-document-render__index-blank-end');
          _blankSpan.innerHTML = "&#9829;blank-id-start".concat(blankMark, "blank-id-end&#9829;&#8593;");
          wrapper.appendChild(_blankSpan);
        }
        ruby.appendChild(hanziSpan);
        ruby.appendChild(rt);
      }
    }, {
      key: "render",
      value: function render() {
        try {
          var shadow = this.attachShadow({
            mode: 'open'
          });
          this.group = document.createElement('span');
          // Attach the created elements to the shadow dom
          shadow.appendChild(this.getStyle());
          shadow.appendChild(this.group);
          this.updateGroupByDataInfo();
        } catch (error) {
          console.log(error);
        }
      }
    }], [{
      key: "observedAttributes",
      get: function get() {
        return ['data-info'];
      }
    }]);
  }(/*#__PURE__*/_wrapNativeSuper(HTMLElement)); // Define the new element
  if (!customElements.get('shiny-blanks')) {
    customElements.define('shiny-blanks', ShinyBlank);
  }
})();