"use strict";

function _typeof(o) { "@babel/helpers - typeof"; return _typeof = "function" == typeof Symbol && "symbol" == typeof Symbol.iterator ? function (o) { return typeof o; } : function (o) { return o && "function" == typeof Symbol && o.constructor === Symbol && o !== Symbol.prototype ? "symbol" : typeof o; }, _typeof(o); }
function _classCallCheck(a, n) { if (!(a instanceof n)) throw new TypeError("Cannot call a class as a function"); }
function _defineProperties(e, r) { for (var t = 0; t < r.length; t++) { var o = r[t]; o.enumerable = o.enumerable || !1, o.configurable = !0, "value" in o && (o.writable = !0), Object.defineProperty(e, _toPropertyKey(o.key), o); } }
function _createClass(e, r, t) { return r && _defineProperties(e.prototype, r), t && _defineProperties(e, t), Object.defineProperty(e, "prototype", { writable: !1 }), e; }
function _toPropertyKey(t) { var i = _toPrimitive(t, "string"); return "symbol" == _typeof(i) ? i : i + ""; }
function _toPrimitive(t, r) { if ("object" != _typeof(t) || !t) return t; var e = t[Symbol.toPrimitive]; if (void 0 !== e) { var i = e.call(t, r || "default"); if ("object" != _typeof(i)) return i; throw new TypeError("@@toPrimitive must return a primitive value."); } return ("string" === r ? String : Number)(t); }
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
(function () {
  function throttle(func, delay) {
    var lastCall = 0;
    return function () {
      var now = new Date().getTime();
      if (now - lastCall < delay) {
        return;
      }
      lastCall = now;
      return func.apply(void 0, arguments);
    };
  }
  function getSpanAndWidthByPunctuation(punctuation, fontSize) {
    // 创建一个隐藏的容器
    var hiddenContainer = document.createElement('div');
    hiddenContainer.style.visibility = 'hidden';
    hiddenContainer.style.position = 'absolute';
    hiddenContainer.style.whiteSpace = 'nowrap'; // 确保宽度准确
    hiddenContainer.style.fontFamily = 'Times New Roman,Songti SC,TimesNewRomanPSMT,SimSong-Regular,SimSun';
    hiddenContainer.style.fontSize = fontSize;
    var dotSpan = document.createElement('span');
    dotSpan.textContent = punctuation;
    hiddenContainer.appendChild(dotSpan);
    // 将隐藏容器添加到body
    document.body.appendChild(hiddenContainer);
    var punctuationSpanWidth = dotSpan.offsetWidth;
    // 从DOM中移除隐藏容器
    document.body.removeChild(hiddenContainer);
    return {
      dotSpan: dotSpan,
      punctuationSpanWidth: punctuationSpanWidth
    };
  }
  var FullLineBlank = /*#__PURE__*/function (_HTMLElement) {
    function FullLineBlank() {
      var _this;
      _classCallCheck(this, FullLineBlank);
      _this = _callSuper(this, FullLineBlank);
      _this.style.display = 'inline';
      _this.style.position = 'static';
      _this.handlePositionChange = throttle(_this.handlePositionChange.bind(_this), 200);
      return _this;
    }
    _inherits(FullLineBlank, _HTMLElement);
    return _createClass(FullLineBlank, [{
      key: "attributeChangedCallback",
      value: function attributeChangedCallback() {
        this.updateContent.call(this);
      }
    }, {
      key: "connectedCallback",
      value: function connectedCallback() {
        this.render();
        window.addEventListener('resize', this.updateContent.bind(this));
        this.addEventListener('positionChange', this.handlePositionChange);
      }
    }, {
      key: "disconnectedCallback",
      value: function disconnectedCallback() {
        this.removeEventListener('positionChange', this.handlePositionChange);
        window.removeEventListener('resize', this.updateContent.bind(this));
      }
    }, {
      key: "handlePositionChange",
      value: function handlePositionChange(e) {
        this.updateContent.call(this);
      }
    }, {
      key: "updateContent",
      value: function updateContent() {
        if (!this.dom) return;
        this.dom.textContent = '';
        if (this.getAttribute('blank-mark')) {
          var blankMark = this.getAttribute('blank-mark');
          var blankSpan = document.createElement('span');
          blankSpan.setAttribute('class', 'metis-document-render__index-blank metis-document-render__index-blank-start');
          blankSpan.innerHTML = "&#9829;blank-id-start".concat(blankMark, "blank-id-end&#9829;&#8595;");
          this.dom.appendChild(blankSpan);
        }
        var lines = +this.getAttribute('data-lines') || 1;
        var placeholder = this.getAttribute('data-placeholder') || '';
        var placeholderInRender = this.getAttribute('data-placeholder-in-render') || '';
        var punctuation = this.getAttribute('data-punctuation') || '';
        var lineHeight = this.getAttribute('data-line-height');
        var parentDom = this.parentNode;
        var blankIndex = this.getAttribute('data-blank-index');
        if (blankIndex && !placeholderInRender) {
          var blankIndexSpan = document.createElement('span');
          blankIndexSpan.innerHTML = blankIndex;
          blankIndexSpan.style = 'font-weight: 900; color: #000; padding-left: 4px;';
          this.dom.appendChild(blankIndexSpan);
        }
        if (!parentDom) return;
        var firstLine = document.createElement('span');
        var parentStyle = window.getComputedStyle(parentDom);
        // 获取标点符号的宽度（用于计算最后一行的实际宽度）
        var _getSpanAndWidthByPun = getSpanAndWidthByPunctuation(punctuation, parentStyle.fontSize),
          punctuationSpanWidth = _getSpanAndWidthByPun.punctuationSpanWidth;
        if (placeholder) {
          firstLine.setAttribute('class', 'first-line line');
          firstLine.innerHTML = '&nbsp;';
        } else {
          firstLine.setAttribute('class', 'first-line line');
          lineHeight && firstLine.setAttribute('style', "line-height: ".concat(lineHeight, "; vertical-align: text-bottom;"));
          firstLine.innerHTML = "&nbsp;<span class=\"first-line-render ".concat(this.getAttribute('emphasized-styling') ? 'emphasized-styling' : '', "\">\n           <span style=\"vertical-align:text-bottom\">").concat('i'.repeat(500), "</span>\n          </span>");
        }
        this.dom.appendChild(firstLine);
        var boxSizing = parentStyle.boxSizing;
        var offsetLeft = parentDom.offsetLeft > this.dom.offsetLeft ? this.dom.offsetLeft : this.dom.offsetLeft - parentDom.offsetLeft;
        if (boxSizing === 'border-box') {
          offsetLeft += parseFloat(parentStyle.padding) + parseFloat(parentStyle.borderLeftWidth);
        } else {
          offsetLeft -= parseFloat(parentStyle.padding) + parseFloat(parentStyle.borderLeftWidth);
        }
        var parentWidth = parentStyle.width === 'auto' ? this.getAttribute('data-first-line-width') || 0 : parseFloat(parentStyle.width);
        // 计算第一行的宽度
        var firstLineCalcWidth = Math.max(0, Math.floor(parentWidth - offsetLeft) - 1);

        // 创建最后一行：需要动态计算宽度
        var lastLine = document.createElement('span');
        lastLine.setAttribute('class', 'line full-line');
        lastLine.innerHTML = '&nbsp;';
        lastLine.style.width = Math.max(0, Math.floor(parentWidth - punctuationSpanWidth) - 1) + 'px';
        // 渲染和编辑器两端用不同方式
        if (placeholder) {
          firstLine.style.width = firstLineCalcWidth + 'px';
          if (firstLineCalcWidth >= 0) {
            this.setAttribute('data-first-line-width', firstLineCalcWidth);
            if (lines > 2) {
              this.dom.innerHTML = this.dom.innerHTML + "<span class=\"line full-line\">&nbsp;</span>".repeat(lines - 2);
              // 插入最后一行
              this.dom.innerHTML += lastLine.outerHTML;
            } else if (lines === 2) {
              // 插入最后一行
              this.dom.innerHTML += lastLine.outerHTML;
            }
          } else {
            if (lines > 2) {
              this.dom.innerHTML = this.dom.innerHTML + "<span class=\"line full-line\">&nbsp;</span>".repeat(lines - 1);
              // 插入最后一行
              this.dom.innerHTML += lastLine.outerHTML;
            } else if (lines === 2) {
              // 插入最后一行
              this.dom.innerHTML += lastLine.outerHTML;
            }
          }
        } else {
          if (lines === 1 && punctuation !== null && punctuation !== void 0 && punctuation.length) {
            if (firstLineCalcWidth <= punctuationSpanWidth) {
              firstLine.style.display = 'block';
              this.dom.innerHTML = this.dom.innerHTML.slice(0, -7) + "<span class=\"full-line-punctuation\" style={line-height: ".concat(parentStyle.lineHeight, ";}>").concat(punctuation, "</span>");
            } else {
              this.dom.innerHTML = this.dom.innerHTML.slice(0, -7) + "<span class=\"full-line-punctuation\" style=\"line-height: ".concat(parentStyle.lineHeight, ";left: ").concat(firstLineCalcWidth - punctuationSpanWidth, "px;right:unset; width: ").concat(punctuationSpanWidth + 1000, "px;\">").concat(punctuation, "</span>") + '</span>';
            }
          }
          // 兼容单行且后面跟有行内元素的情况
          this.dom.innerHTML += '<br/>';
          var curDom = parentDom;
          while (curDom && window.getComputedStyle(curDom).display === 'inline') {
            curDom = curDom.parentElement;
          }
          if (curDom) {
            curDom.style.overflow = 'hidden';
          }
          var isTd = false;
          // 解决table里增加full-line-blank时，full-line-blank的宽度不受控制的问题
          if (curDom.tagName === 'TD') {
            isTd = true;
          }
          this.dom.innerHTML += "<span class=\"line full-line ".concat(isTd ? '' : 'full-line-render', " ").concat(this.getAttribute('emphasized-styling') ? 'emphasized-styling' : '', "\">\n            <span style=\"").concat(lineHeight ? "line-height: ".concat(lineHeight, ";vertical-align:text-bottom") : '', "\">").concat(isTd ? '&nbsp;' : '&nbsp;'.repeat(500), "</span>\n          </span>").repeat(lines - 1);
          // 两行以上的情况
          if (punctuation !== null && punctuation !== void 0 && punctuation.length && lines > 1) {
            this.dom.innerHTML = this.dom.innerHTML.slice(0, -7) + "<span class=\"full-line-punctuation\" style={line-height: ".concat(parentStyle.lineHeight, ";}>").concat(punctuation, "</span>") + '</span>';
          }
        }
        if (this.getAttribute('blank-mark')) {
          var _blankMark = this.getAttribute('blank-mark');
          var _blankSpan = document.createElement('span');
          _blankSpan.setAttribute('class', 'metis-document-render__index-blank metis-document-render__index-blank-end');
          _blankSpan.innerHTML = "&#9829;blank-id-start".concat(_blankMark, "blank-id-end&#9829;&#8593;");
          this.dom.appendChild(_blankSpan);
        }
        if (placeholder) {
          if (lines === 1) {
            this.dom.querySelector('.first-line').textContent = placeholder;
            // 当只有一行且有标点符号时，为避免后面的元素覆盖::after，伪元素覆盖通行下划线的末尾
            if (punctuation !== null && punctuation !== void 0 && punctuation.length) {
              // 设置伪元素的宽度
              var style = document.createElement('style');
              style.innerHTML = "\n            .first-line::after{\n            content: \"".concat(Number(this.getAttribute('data-lines')) === 1 ? this.getAttribute('data-punctuation') : '', "\";\n            position: absolute;\n            width: ").concat(punctuationSpanWidth, "px;\n            right: ").concat(punctuationSpanWidth, "px;\n            top: 1px;\n            background: white;\n            color: rgba(0, 0, 0, 0.85);\n            transform: translateX(100%);\n            }");
              this.dom.appendChild(style);
            }
          } else {
            // 在中间一个行
            this.dom.querySelector(".full-line:nth-of-type(".concat(Math.max(2, Math.ceil(lines / 2)), ")")).textContent = placeholder;
          }
          this.dom.classList.add('with-placeholder');
        }
        if (placeholderInRender) {
          var holderLineIndex = lines === 1 ? 0 : Math.max(2, Math.ceil(lines / 2)) - 1;
          var holderLine = this.dom.querySelectorAll('.line')[holderLineIndex];
          if (holderLineIndex === 0) {
            // 第一行
            holderLine.innerHTML += "<span class=\"full-line-index-in-render\" style=\"left: ".concat(firstLineCalcWidth / 2, "px;\">").concat(placeholderInRender, "</span>");
          } else if (holderLineIndex === lines - 1) {
            // 最后一行
            holderLine.innerHTML += "<span class=\"full-line-index-in-render\" style=\"left: ".concat((parentWidth - punctuationSpanWidth) / 2, "px; right: unset\">").concat(placeholderInRender, "</span>");
          } else {
            holderLine.innerHTML += "<span class=\"full-line-index-in-render\">".concat(placeholderInRender, "</span>");
          }
        }
      }
    }, {
      key: "getStyle",
      value: function getStyle() {
        var style = document.createElement('style');
        style.textContent = "\n      .full-line-blank {\n        font-family: Times New Roman,Songti SC,TimesNewRomanPSMT,SimSong-Regular,SimSun;\n      }\n      .first-line{\n        display:inline-block;\n        vertical-align: baseline;\n        text-align: center;\n        position: relative;\n      }\n      .first-line-render{\n        display: block;\n        white-space: nowrap;\n        color: transparent;\n        overflow: hidden;\n        top: 0;\n        position: absolute;\n        left: 0;\n        text-decoration: underline;\n        text-decoration-color: #182129;\n        text-decoration-thickness: 1px;\n      }\n      .line{\n        position: relative;\n      }\n      .emphasized-styling::after {\n        content: '';\n        position: absolute;\n        top: 2px;\n        bottom: 2px;\n        left: 2px;\n        right: 2px;\n        background: rgba(172, 255, 48, 0.5);\n        border-bottom: 0 none;\n        z-index: 999;\n        width: 9999px;\n      }\n      ".concat(this.getAttribute('with-border') ? "\n        .line::after {\n          position: absolute;\n          content: '';\n          top: 2px;\n          bottom: 2px;\n          left: 2px;\n          right: 2px;\n          background: green;\n          border-bottom: 0 none;\n          z-index: 9999;\n          width: 9999px;\n        }\n        " : '', "\n\n      .full-line{\n        display:block;\n        width:100%;\n        text-align: center;\n        border-bottom: 1px solid #182129;\n      }\n\n      .full-line-render {\n        text-decoration: underline;\n        text-decoration-color: #182129;\n        text-decoration-thickness: 1px;\n        white-space: nowrap;\n        overflow: hidden;\n        border-bottom: 0;\n      }\n      .with-placeholder .first-line,\n      .with-placeholder .line{\n        border-bottom: var(--full-line-with-placeholder-border, 1px solid #0071FD);\n        opacity: 0.8;\n        color: var(--full-line-with-placeholder-color, #0071FD);\n      }\n      .with-placeholder .full-line:last-child::after {\n        content: \"").concat(this.getAttribute('data-punctuation'), "\";\n        position: absolute;\n        right: 0;\n        color: rgba(0, 0, 0, 0.85);\n        transform: translateX(100%);\n      }\n      .metis-document-render__index-blank {\n        color: white;\n        transform: scale(0.001);\n        position: absolute;\n        white-space: nowrap;\n      }\n      .metis-document-render__index-blank-start {\n        left: 0;\n        top: 40%;\n        transform: translateY(-50%) scale(0.001);\n        transform-origin: center left;\n      }\n      .metis-document-render__index-blank-end {\n        left: 0;\n        top: 60%;\n        transform: translateY(-50%) scale(0.001);\n        transform-origin: center left;\n      }\n      .full-line-punctuation {\n        position: absolute;\n        right: 0;\n        bottom: -1px;\n        background: #fff;\n        z-index: 9999;\n        text-align: left;\n        white-space: nowrap;\n      }\n      .full-line-index-in-render {\n        position: absolute;\n        white-space: nowrap;\n        bottom: 0;\n        left: 0;\n        right: 0;\n        text-align: center;\n        user-select: none;\n      }\n  ");
        return style;
      }
    }, {
      key: "render",
      value: function render() {
        try {
          var shadow = this.attachShadow({
            mode: 'open'
          });
          this.dom = document.createElement('span');
          this.dom.setAttribute('class', 'full-line-blank');
          shadow.appendChild(this.dom);
          shadow.appendChild(this.getStyle());
          this.updateContent();
        } catch (error) {
          console.log(error);
        }
      }
    }], [{
      key: "observedAttributes",
      get: function get() {
        return ['data-lines', 'data-placeholder', 'data-punctuation', 'data-placeholder-in-render', 'data-line-height', 'data-blank-index'];
      }
    }]);
  }(/*#__PURE__*/_wrapNativeSuper(HTMLElement)); // Define the new element
  if (!customElements.get('full-line-blank')) {
    customElements.define('full-line-blank', FullLineBlank);
  }
})();