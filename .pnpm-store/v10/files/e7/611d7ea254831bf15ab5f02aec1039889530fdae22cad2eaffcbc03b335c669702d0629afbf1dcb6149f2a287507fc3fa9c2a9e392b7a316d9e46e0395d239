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
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
var react_1 = __importStar(require("react"));
var context_js_1 = require("../context.js");
var usePaintHue_js_1 = __importDefault(require("../hooks/usePaintHue.js"));
var utils_js_1 = require("../utils/utils.js");
var tinycolor2_1 = __importDefault(require("tinycolor2"));
var Hue = function () {
    var barRef = (0, react_1.useRef)(null);
    var _a = (0, context_js_1.usePicker)(), config = _a.config, handleChange = _a.handleChange, squareWidth = _a.squareWidth, hc = _a.hc, setHc = _a.setHc, pickerIdSuffix = _a.pickerIdSuffix;
    var _b = (0, react_1.useState)(false), dragging = _b[0], setDragging = _b[1];
    var barSize = config.barSize;
    (0, usePaintHue_js_1.default)(barRef, squareWidth);
    var stopDragging = function () {
        setDragging(false);
    };
    var handleDown = function () {
        setDragging(true);
    };
    var handleHue = function (e) {
        var newHue = (0, utils_js_1.getHandleValue)(e, barSize) * 3.6;
        var tinyHsv = (0, tinycolor2_1.default)({ h: newHue, s: hc === null || hc === void 0 ? void 0 : hc.s, v: hc === null || hc === void 0 ? void 0 : hc.v });
        var _a = tinyHsv.toRgb(), r = _a.r, g = _a.g, b = _a.b;
        handleChange("rgba(".concat(r, ", ").concat(g, ", ").concat(b, ", ").concat(hc.a, ")"));
        setHc(__assign(__assign({}, hc), { h: newHue }));
    };
    var handleMove = function (e) {
        if (dragging) {
            handleHue(e);
        }
    };
    var handleClick = function (e) {
        if (!dragging) {
            handleHue(e);
        }
    };
    (0, react_1.useEffect)(function () {
        var handleUp = function () {
            stopDragging();
        };
        window.addEventListener('mouseup', handleUp);
        return function () {
            window.removeEventListener('mouseup', handleUp);
        };
    }, []);
    return (react_1.default.createElement("div", { style: {
            height: 14,
            marginTop: 17,
            marginBottom: 4,
            cursor: 'ew-resize',
            position: 'relative',
        }, onMouseMove: function (e) { return handleMove(e); }, id: "rbgcp-hue-wrap".concat(pickerIdSuffix) },
        react_1.default.createElement("div", { tabIndex: 0, role: "button", 
            // className="rbgcp-handle rbgcp-handle-hue"
            style: {
                border: '2px solid white',
                borderRadius: '50%',
                boxShadow: '0px 0px 3px rgba(0, 0, 0, 0.5)',
                width: '18px',
                height: '18px',
                zIndex: 1000,
                transition: 'all 10ms linear',
                position: 'absolute',
                left: (hc === null || hc === void 0 ? void 0 : hc.h) * ((squareWidth - 18) / 360),
                top: -2,
                cursor: 'ew-resize',
                boxSizing: 'border-box',
            }, onMouseDown: handleDown, id: "rbgcp-hue-handle".concat(pickerIdSuffix) }),
        react_1.default.createElement("canvas", { ref: barRef, height: "14px", 
            // className="rbgcp-hue-bar"
            width: "".concat(squareWidth, "px"), onClick: function (e) { return handleClick(e); }, id: "rbgcp-hue-bar".concat(pickerIdSuffix), style: {
                borderRadius: 14,
                position: 'relative',
                verticalAlign: 'top',
            } })));
};
exports.default = Hue;
