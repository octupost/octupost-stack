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
/* eslint-disable jsx-a11y/no-static-element-interactions */
import { computePickerPosition, computeSquareXY } from '../utils/utils.js';
import React, { useRef, useState, useEffect } from 'react';
import usePaintSquare from '../hooks/usePaintSquare.js';
import { usePicker } from '../context.js';
import throttle from 'lodash.throttle';
import tinycolor from 'tinycolor2';
var Square = function () {
    var _a, _b;
    var _c = usePicker(), hc = _c.hc, config = _c.config, squareWidth = _c.squareWidth, squareHeight = _c.squareHeight, handleChange = _c.handleChange, defaultStyles = _c.defaultStyles, pickerIdSuffix = _c.pickerIdSuffix;
    var crossSize = config.crossSize;
    var _d = useState(false), dragging = _d[0], setDragging = _d[1];
    var canvas = useRef(null);
    var _e = computeSquareXY(hc === null || hc === void 0 ? void 0 : hc.s, (hc === null || hc === void 0 ? void 0 : hc.v) * 100, squareWidth, squareHeight, crossSize), x = _e[0], y = _e[1];
    var _f = useState({ x: x, y: y }), dragPos = _f[0], setDragPos = _f[1];
    usePaintSquare(canvas, hc === null || hc === void 0 ? void 0 : hc.h, squareWidth, squareHeight);
    useEffect(function () {
        if (!dragging) {
            setDragPos({ x: (hc === null || hc === void 0 ? void 0 : hc.v) === 0 ? dragPos.x : x, y: y });
        }
    }, [x, y]);
    var handleColor = function (e) {
        var onMouseMove = throttle(function () {
            var _a = computePickerPosition(e, crossSize), x = _a[0], y = _a[1];
            if (x && y) {
                var x1 = Math.min(x + crossSize / 2, squareWidth - 1);
                var y1 = Math.min(y + crossSize / 2, squareHeight - 1);
                var newS = (x1 / squareWidth) * 100;
                var newY = 100 - (y1 / squareHeight) * 100;
                setDragPos({ x: newY === 0 ? dragPos === null || dragPos === void 0 ? void 0 : dragPos.x : x, y: y });
                var updated = tinycolor("hsva(".concat(hc === null || hc === void 0 ? void 0 : hc.h, ", ").concat(newS, "%, ").concat(newY, "%, ").concat(hc === null || hc === void 0 ? void 0 : hc.a, ")"));
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
    useEffect(function () {
        var handleUp = function () {
            stopDragging();
        };
        window.addEventListener('mouseup', handleUp);
        return function () {
            window.removeEventListener('mouseup', handleUp);
        };
    }, []);
    return (React.createElement("div", { style: { position: 'relative', marginBottom: 12 }, id: "rbgcp-square-wrapper".concat(pickerIdSuffix) },
        React.createElement("div", { onMouseUp: stopDragging, onTouchEnd: stopDragging, onMouseDown: handleCanvasDown, onTouchStart: handleCanvasDown, onMouseMove: function (e) { return handleMove(e); }, id: "rbgcp-square".concat(pickerIdSuffix), style: { position: 'relative', cursor: 'ew-cross' } },
            React.createElement("div", { style: __assign(__assign(__assign({}, defaultStyles.rbgcpHandle), { transform: "translate(".concat((_a = dragPos === null || dragPos === void 0 ? void 0 : dragPos.x) !== null && _a !== void 0 ? _a : 0, "px, ").concat((_b = dragPos === null || dragPos === void 0 ? void 0 : dragPos.y) !== null && _b !== void 0 ? _b : 0, "px)") }), (dragging ? { transition: '' } : {})), onMouseDown: handleMouseDown, id: "rbgcp-square-handle".concat(pickerIdSuffix) }),
            React.createElement("div", { style: __assign(__assign({}, defaultStyles.rbgcpCanvasWrapper), { height: squareHeight }), id: "rbgcp-square-canvas-wrapper".concat(pickerIdSuffix), 
                // className="rbgcp-canvas-wrapper"
                onClick: function (e) { return handleClick(e); } },
                React.createElement("canvas", { ref: canvas, 
                    // className="rbgcp-canvas"
                    width: "".concat(squareWidth, "px"), height: "".concat(squareHeight, "px"), id: "rbgcp-square-canvas".concat(pickerIdSuffix) })))));
};
export default Square;
