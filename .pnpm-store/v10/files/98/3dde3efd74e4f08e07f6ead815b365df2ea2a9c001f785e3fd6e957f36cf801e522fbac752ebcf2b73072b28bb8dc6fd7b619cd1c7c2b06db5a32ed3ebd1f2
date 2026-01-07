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
/* eslint-disable react/jsx-no-leaked-render */
/* eslint-disable jsx-a11y/no-static-element-interactions */
var react_1 = __importStar(require("react"));
var Portal_js_1 = __importDefault(require("./Portal.js"));
var html2canvas_1 = __importDefault(require("html2canvas"));
var styles_js_1 = require("../styles/styles.js");
var tinycolor2_1 = __importDefault(require("tinycolor2"));
var context_js_1 = require("../context.js");
var DropperIcon = function (_a) {
    var color = _a.color;
    var defaultStyles = (0, context_js_1.usePicker)().defaultStyles;
    var col = color !== null && color !== void 0 ? color : '';
    return (react_1.default.createElement("svg", { xmlns: "http://www.w3.org/2000/svg", viewBox: "0 0 20 20", style: { width: 16 } },
        react_1.default.createElement("path", { strokeLinecap: "round", strokeLinejoin: "round", style: __assign(__assign({ fill: 'none', strokeWidth: '1.4px' }, defaultStyles.rbgcpControlIcon), (col && { stroke: col })), d: "M15.6,7h0L7.78,14.86c-.37.37-1.61.38-2,.75s-.5,1.53-.76,2a3.53,3.53,0,0,1-.52.52,1.6,1.6,0,0,1-2.27-.06l-.32-.32a1.61,1.61,0,0,1-.06-2.27A3.25,3.25,0,0,1,2.4,15c.47-.26,1.65-.35,2-.73s.34-1.64.71-2c1.68-1.73,5.61-5.65,7.91-7.93h0l1.14,1.38L15.6,7Z" }),
        react_1.default.createElement("polygon", { strokeLinecap: "round", strokeLinejoin: "round", style: __assign(__assign({ strokeWidth: '1.4px' }, defaultStyles.rbgcpControlIcon2), (col && { stroke: col, fill: col })), points: "15.7 8.87 11.13 4.29 12.69 2.73 17.25 7.31 15.7 8.87" }),
        react_1.default.createElement("path", { strokeLinecap: "round", strokeLinejoin: "round", style: __assign(__assign({ strokeWidth: '1.4px' }, defaultStyles.rbgcpControlIcon2), (col && { stroke: col, fill: col })), d: "M18.18,3.71,16.36,5.53a1.33,1.33,0,0,1-1.88,0h0a1.34,1.34,0,0,1,0-1.89l1.81-1.82a1.34,1.34,0,0,1,1.89,0h0A1.34,1.34,0,0,1,18.18,3.71Z" })));
};
var Dropper = function (_a) {
    var onSelect = _a.onSelect;
    var defaultStyles = (0, context_js_1.usePicker)().defaultStyles;
    var _b = (0, react_1.useState)(null), pickerCanvas = _b[0], setPickerCanvas = _b[1];
    var _c = (0, react_1.useState)(false), coverUp = _c[0], setCoverUp = _c[1];
    var _d = (0, react_1.useState)(false), isPicking = _d[0], setIsPicking = _d[1];
    var takePick = function () {
        var root = document.getElementById('root');
        setCoverUp(true);
        // @ts-expect-error some error with this imported packages types
        (0, html2canvas_1.default)(root).then(function (canvas) {
            var blankCanvas = document.createElement('canvas');
            var ctx = blankCanvas.getContext('2d', { willReadFrequently: true });
            if (root && ctx) {
                blankCanvas.width = root.offsetWidth * 2;
                blankCanvas.height = root.offsetHeight * 2;
                ctx.drawImage(canvas, 0, 0);
            }
            setPickerCanvas(ctx);
        });
    };
    var getColorLegacy = function (e) {
        e.stopPropagation();
        if (pickerCanvas) {
            var pageX = e.pageX, pageY = e.pageY;
            var x1 = pageX * 2;
            var y1 = pageY * 2;
            var rgb = pickerCanvas.getImageData(x1, y1, 1, 1).data;
            onSelect("rgba(".concat(rgb[0], ", ").concat(rgb[1], ", ").concat(rgb[2], ", 1)"));
        }
        setIsPicking(false);
        setCoverUp(false);
    };
    var getEyeDrop = function () {
        setIsPicking(true);
        // @ts-expect-error - ts does not evaluate for window.EyeDropper
        if (!window.EyeDropper) {
            takePick();
        }
        else {
            // @ts-expect-error - ts does not evaluate for window.EyeDropper
            var eyeDropper = new window.EyeDropper();
            var abortController = new window.AbortController();
            eyeDropper
                .open({ signal: abortController.signal })
                .then(function (result) {
                var tinyHex = (0, tinycolor2_1.default)(result.sRGBHex);
                var _a = tinyHex.toRgb(), r = _a.r, g = _a.g, b = _a.b;
                onSelect("rgba(".concat(r, ", ").concat(g, ", ").concat(b, ", 1)"));
                setIsPicking(false);
            })
                .catch(function (e) {
                console.log(e);
                setIsPicking(false);
            });
        }
    };
    return (react_1.default.createElement("div", null,
        react_1.default.createElement("div", { onClick: getEyeDrop, id: "rbgcp-eyedropper-btn", style: __assign(__assign({}, defaultStyles.rbgcpEyedropperBtn), (0, styles_js_1.controlBtnStyles)(coverUp, defaultStyles)) },
            react_1.default.createElement(DropperIcon, { color: isPicking ? 'rgb(86, 140, 245)' : '' })),
        coverUp && (react_1.default.createElement(Portal_js_1.default, null,
            react_1.default.createElement("div", { onClick: function (e) { return getColorLegacy(e); }, style: defaultStyles.rbgcpEyedropperCover })))));
};
exports.default = Dropper;
