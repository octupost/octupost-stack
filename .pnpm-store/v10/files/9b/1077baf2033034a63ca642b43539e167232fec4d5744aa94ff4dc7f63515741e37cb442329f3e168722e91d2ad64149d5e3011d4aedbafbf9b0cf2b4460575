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
import React, { useState, useEffect } from 'react';
import { usePicker } from '../context.js';
import { getHandleValue } from '../utils/utils.js';
var Opacity = function () {
    var _a = usePicker(), config = _a.config, _b = _a.hc, hc = _b === void 0 ? {} : _b, squareWidth = _a.squareWidth, handleChange = _a.handleChange, defaultStyles = _a.defaultStyles, pickerIdSuffix = _a.pickerIdSuffix;
    var _c = useState(false), dragging = _c[0], setDragging = _c[1];
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
        var newO = getHandleValue(e, barSize) / 100;
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
    useEffect(function () {
        var handleUp = function () {
            stopDragging();
        };
        window.addEventListener('mouseup', handleUp);
        return function () {
            window.removeEventListener('mouseup', handleUp);
        };
    }, []);
    return (React.createElement("div", { onMouseDown: handleDown, onMouseMove: function (e) { return handleMove(e); }, style: {
            height: 14,
            marginTop: 17,
            marginBottom: 4,
            cursor: 'ew-resize',
            position: 'relative',
        }, id: "rbgcp-opacity-wrapper".concat(pickerIdSuffix) },
        React.createElement("div", { 
            // className="rbgcp-opacity-checkered"
            id: "rbgcp-opacity-checkered-bg".concat(pickerIdSuffix), style: __assign(__assign({}, defaultStyles.rbgcpCheckered), { width: '100%', height: 14 }) }),
        React.createElement("div", { 
            // className="rbgcp-handle rbgcp-handle-opacity"
            id: "rbgcp-opacity-handle".concat(pickerIdSuffix), style: __assign(__assign({}, defaultStyles.rbgcpHandle), { left: left * (hc === null || hc === void 0 ? void 0 : hc.a), top: -2 }) }),
        React.createElement("div", { style: __assign(__assign({}, defaultStyles.rbgcpOpacityOverlay), { background: bg }), id: "rbgcp-opacity-overlay".concat(pickerIdSuffix), 
            // className="rbgcp-opacity-overlay"
            onClick: function (e) { return handleClick(e); } })));
};
export default Opacity;
