"use strict";
var __assign = (this && this.__assign) || function () {
    __assign = Object.assign || function(t) {
        for (var s, i = 1, n = arguments.length; i < n; i++) {
            s = arguments[i];
            for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p))
                t[p] = s[p];
        }
        return t;
    };
    return __assign.apply(this, arguments);
};
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
/* eslint-disable jsx-a11y/no-static-element-interactions */
var react_1 = __importStar(require("react"));
var context_js_1 = require("../context.js");
var utils_js_1 = require("../utils/utils.js");
var Opacity = function () {
    var _a = (0, context_js_1.usePicker)(), config = _a.config, _b = _a.hc, hc = _b === void 0 ? {} : _b, squareWidth = _a.squareWidth, handleChange = _a.handleChange, defaultStyles = _a.defaultStyles, pickerIdSuffix = _a.pickerIdSuffix;
    var _c = (0, react_1.useState)(false), dragging = _c[0], setDragging = _c[1];
    var r = hc.r, g = hc.g, b = hc.b;
    var bg = "linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(".concat(r, ",").concat(g, ",").concat(b, ",.5) 100%)");
    var barSize = config.barSize;
    var stopDragging = function () {
        setDragging(false);
    };
    var handleDown = function () {
        setDragging(true);
    };
    var handleOpacity = function (e) {
        var newO = (0, utils_js_1.getHandleValue)(e, barSize) / 100;
        var newColor = "rgba(".concat(r, ", ").concat(g, ", ").concat(b, ", ").concat(newO, ")");
        handleChange(newColor);
    };
    var handleMove = function (e) {
        if (dragging) {
            handleOpacity(e);
        }
    };
    var handleClick = function (e) {
        if (!dragging) {
            handleOpacity(e);
        }
    };
    var left = squareWidth - 18;
    (0, react_1.useEffect)(function () {
        var handleUp = function () {
            stopDragging();
        };
        window.addEventListener('mouseup', handleUp);
        return function () {
            window.removeEventListener('mouseup', handleUp);
        };
    }, []);
    return (react_1.default.createElement("div", { onMouseDown: handleDown, onMouseMove: function (e) { return handleMove(e); }, style: {
            height: 14,
            marginTop: 17,
            marginBottom: 4,
            cursor: 'ew-resize',
            position: 'relative',
        }, id: "rbgcp-opacity-wrapper".concat(pickerIdSuffix) },
        react_1.default.createElement("div", { 
            // className="rbgcp-opacity-checkered"
            id: "rbgcp-opacity-checkered-bg".concat(pickerIdSuffix), style: __assign(__assign({}, defaultStyles.rbgcpCheckered), { width: '100%', height: 14 }) }),
        react_1.default.createElement("div", { 
            // className="rbgcp-handle rbgcp-handle-opacity"
            id: "rbgcp-opacity-handle".concat(pickerIdSuffix), style: __assign(__assign({}, defaultStyles.rbgcpHandle), { left: left * (hc === null || hc === void 0 ? void 0 : hc.a), top: -2 }) }),
        react_1.default.createElement("div", { style: __assign(__assign({}, defaultStyles.rbgcpOpacityOverlay), { background: bg }), id: "rbgcp-opacity-overlay".concat(pickerIdSuffix), 
            // className="rbgcp-opacity-overlay"
            onClick: function (e) { return handleClick(e); } })));
};
exports.default = Opacity;
