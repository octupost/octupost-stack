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
/* eslint-disable jsx-a11y/no-static-element-interactions */
var utils_js_1 = require("../utils/utils.js");
var react_1 = __importStar(require("react"));
var usePaintSquare_js_1 = __importDefault(require("../hooks/usePaintSquare.js"));
var context_js_1 = require("../context.js");
var lodash_throttle_1 = __importDefault(require("lodash.throttle"));
var tinycolor2_1 = __importDefault(require("tinycolor2"));
var Square = function () {
    var _a, _b;
    var _c = (0, context_js_1.usePicker)(), hc = _c.hc, config = _c.config, squareWidth = _c.squareWidth, squareHeight = _c.squareHeight, handleChange = _c.handleChange, defaultStyles = _c.defaultStyles, pickerIdSuffix = _c.pickerIdSuffix;
    var crossSize = config.crossSize;
    var _d = (0, react_1.useState)(false), dragging = _d[0], setDragging = _d[1];
    var canvas = (0, react_1.useRef)(null);
    var _e = (0, utils_js_1.computeSquareXY)(hc === null || hc === void 0 ? void 0 : hc.s, (hc === null || hc === void 0 ? void 0 : hc.v) * 100, squareWidth, squareHeight, crossSize), x = _e[0], y = _e[1];
    var _f = (0, react_1.useState)({ x: x, y: y }), dragPos = _f[0], setDragPos = _f[1];
    (0, usePaintSquare_js_1.default)(canvas, hc === null || hc === void 0 ? void 0 : hc.h, squareWidth, squareHeight);
    (0, react_1.useEffect)(function () {
        if (!dragging) {
            setDragPos({ x: (hc === null || hc === void 0 ? void 0 : hc.v) === 0 ? dragPos.x : x, y: y });
        }
    }, [x, y]);
    var handleColor = function (e) {
        var onMouseMove = (0, lodash_throttle_1.default)(function () {
            var _a = (0, utils_js_1.computePickerPosition)(e, crossSize), x = _a[0], y = _a[1];
            if (x && y) {
                var x1 = Math.min(x + crossSize / 2, squareWidth - 1);
                var y1 = Math.min(y + crossSize / 2, squareHeight - 1);
                var newS = (x1 / squareWidth) * 100;
                var newY = 100 - (y1 / squareHeight) * 100;
                setDragPos({ x: newY === 0 ? dragPos === null || dragPos === void 0 ? void 0 : dragPos.x : x, y: y });
                var updated = (0, tinycolor2_1.default)("hsva(".concat(hc === null || hc === void 0 ? void 0 : hc.h, ", ").concat(newS, "%, ").concat(newY, "%, ").concat(hc === null || hc === void 0 ? void 0 : hc.a, ")"));
                handleChange(updated.toRgbString());
            }
        }, 250);
        onMouseMove();
    };
    var stopDragging = function () {
        setDragging(false);
    };
    var handleMove = function (e) {
        if (dragging) {
            handleColor(e);
        }
    };
    // const handleTouchMove = (e: any) => {
    //   if (dragging && isMobile) {
    //     document.body.style.overflow = 'hidden'
    //     handleColor(e)
    //   }
    // }
    var handleClick = function (e) {
        if (!dragging) {
            handleColor(e);
        }
    };
    var handleMouseDown = function () {
        setDragging(true);
    };
    var handleCanvasDown = function (e) {
        setDragging(true);
        handleColor(e);
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
    return (react_1.default.createElement("div", { style: { position: 'relative', marginBottom: 12 }, id: "rbgcp-square-wrapper".concat(pickerIdSuffix) },
        react_1.default.createElement("div", { onMouseUp: stopDragging, onTouchEnd: stopDragging, onMouseDown: handleCanvasDown, onTouchStart: handleCanvasDown, onMouseMove: function (e) { return handleMove(e); }, id: "rbgcp-square".concat(pickerIdSuffix), style: { position: 'relative', cursor: 'ew-cross' } },
            react_1.default.createElement("div", { style: __assign(__assign(__assign({}, defaultStyles.rbgcpHandle), { transform: "translate(".concat((_a = dragPos === null || dragPos === void 0 ? void 0 : dragPos.x) !== null && _a !== void 0 ? _a : 0, "px, ").concat((_b = dragPos === null || dragPos === void 0 ? void 0 : dragPos.y) !== null && _b !== void 0 ? _b : 0, "px)") }), (dragging ? { transition: '' } : {})), onMouseDown: handleMouseDown, id: "rbgcp-square-handle".concat(pickerIdSuffix) }),
            react_1.default.createElement("div", { style: __assign(__assign({}, defaultStyles.rbgcpCanvasWrapper), { height: squareHeight }), id: "rbgcp-square-canvas-wrapper".concat(pickerIdSuffix), 
                // className="rbgcp-canvas-wrapper"
                onClick: function (e) { return handleClick(e); } },
                react_1.default.createElement("canvas", { ref: canvas, 
                    // className="rbgcp-canvas"
                    width: "".concat(squareWidth, "px"), height: "".concat(squareHeight, "px"), id: "rbgcp-square-canvas".concat(pickerIdSuffix) })))));
};
exports.default = Square;
