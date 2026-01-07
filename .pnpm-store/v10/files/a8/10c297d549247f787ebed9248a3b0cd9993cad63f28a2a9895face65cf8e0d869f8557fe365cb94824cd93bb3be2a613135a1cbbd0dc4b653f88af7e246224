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
import React, { useState, useRef, useEffect } from 'react';
import { getHandleValue } from '../utils/utils.js';
import { usePicker } from '../context.js';
import { usePaintSat, usePaintLight, usePaintBright, } from '../hooks/usePaintHue.js';
import tinycolor from 'tinycolor2';
var AdvBar = function (_a) {
    var value = _a.value, reffy = _a.reffy, label = _a.label, config = _a.config, callback = _a.callback, squareWidth = _a.squareWidth, openAdvanced = _a.openAdvanced, defaultStyles = _a.defaultStyles, pickerIdSuffix = _a.pickerIdSuffix;
    var barSize = config.barSize;
    var _b = useState(false), dragging = _b[0], setDragging = _b[1];
    var _c = useState(2), handleTop = _c[0], setHandleTop = _c[1];
    var left = value * (squareWidth - 18);
    useEffect(function () {
        var _a;
        setHandleTop(((_a = reffy === null || reffy === void 0 ? void 0 : reffy.current) === null || _a === void 0 ? void 0 : _a.offsetTop) - 2);
    }, [openAdvanced, reffy]);
    var stopDragging = function () {
        setDragging(false);
    };
    var handleMove = function (e) {
        if (dragging) {
            callback(getHandleValue(e, barSize));
        }
    };
    var handleClick = function (e) {
        if (!dragging) {
            callback(getHandleValue(e, barSize));
        }
    };
    var handleDown = function () {
        setDragging(true);
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
    return (React.createElement("div", { style: { width: '100%', padding: '3px 0px 3px 0px' } },
        React.createElement("div", { onMouseMove: function (e) { return handleMove(e); }, 
            // className="rbgcp-advanced-bar-wrap"
            style: { cursor: 'resize', position: 'relative' }, id: "rbgcp-advanced-bar-".concat(label, "-wrapper").concat(pickerIdSuffix) },
            React.createElement("div", { style: __assign({ left: left, top: handleTop }, defaultStyles.rbgcpHandle), id: "rbgcp-advanced-bar-".concat(label, "-handle").concat(pickerIdSuffix), 
                // className="rbgcp-advanced-bar-handle"
                onMouseDown: handleDown, role: "button", tabIndex: 0 }),
            React.createElement("div", { style: {
                    textAlign: 'center',
                    color: '#fff',
                    fontSize: 12,
                    fontWeight: 500,
                    lineHeight: 1,
                    position: 'absolute',
                    left: '50%',
                    transform: 'translate(-50%, 0%)',
                    top: handleTop + 2,
                    zIndex: 10,
                    textShadow: '1px 1px 1px rgba(0,0,0,.6)',
                }, id: "rbgcp-advanced-bar-".concat(label, "-label").concat(pickerIdSuffix), 
                // className="rbgcp-advanced-bar-label"
                onMouseMove: function (e) { return handleMove(e); }, onClick: function (e) { return handleClick(e); }, tabIndex: 0, role: "button", onKeyDown: function () {
                    return;
                } }, label),
            React.createElement("canvas", { ref: reffy, height: "14px", width: "".concat(squareWidth, "px"), onClick: function (e) { return handleClick(e); }, 
                // className="rbgcp-advanced-bar-canvas"
                style: { position: 'relative', borderRadius: 14 }, id: "rbgcp-advanced-bar-".concat(label, "-canvas").concat(pickerIdSuffix) }))));
};
var AdvancedControls = function (_a) {
    var openAdvanced = _a.openAdvanced;
    var _b = usePicker(), config = _b.config, tinyColor = _b.tinyColor, handleChange = _b.handleChange, squareWidth = _b.squareWidth, hc = _b.hc, defaultStyles = _b.defaultStyles, pickerIdSuffix = _b.pickerIdSuffix;
    var _c = tinyColor.toHsl(), s = _c.s, l = _c.l;
    var satRef = useRef(null);
    var lightRef = useRef(null);
    var brightRef = useRef(null);
    usePaintSat(satRef, hc === null || hc === void 0 ? void 0 : hc.h, l * 100, squareWidth);
    usePaintLight(lightRef, hc === null || hc === void 0 ? void 0 : hc.h, s * 100, squareWidth);
    usePaintBright(brightRef, hc === null || hc === void 0 ? void 0 : hc.h, s * 100, squareWidth);
    var satDesat = function (value) {
        var _a = tinycolor({ h: hc === null || hc === void 0 ? void 0 : hc.h, s: value / 100, l: l }).toRgb(), r = _a.r, g = _a.g, b = _a.b;
        handleChange("rgba(".concat(r, ",").concat(g, ",").concat(b, ",").concat(hc === null || hc === void 0 ? void 0 : hc.a, ")"));
    };
    var setLight = function (value) {
        var _a = tinycolor({ h: hc === null || hc === void 0 ? void 0 : hc.h, s: s, l: value / 100 }).toRgb(), r = _a.r, g = _a.g, b = _a.b;
        handleChange("rgba(".concat(r, ",").concat(g, ",").concat(b, ",").concat(hc === null || hc === void 0 ? void 0 : hc.a, ")"));
    };
    var setBright = function (value) {
        var _a = tinycolor({
            h: hc === null || hc === void 0 ? void 0 : hc.h,
            s: (hc === null || hc === void 0 ? void 0 : hc.s) * 100,
            v: value,
        }).toRgb(), r = _a.r, g = _a.g, b = _a.b;
        handleChange("rgba(".concat(r, ",").concat(g, ",").concat(b, ",").concat(hc === null || hc === void 0 ? void 0 : hc.a, ")"));
    };
    return (React.createElement("div", { style: {
            width: '100%',
            height: openAdvanced ? 98 : 0,
            transition: 'all 120ms linear',
        }, id: "rbgcp-advanced-controls-wrapper".concat(pickerIdSuffix) },
        React.createElement("div", { style: {
                paddingTop: 11,
                display: openAdvanced ? 'flex' : 'none',
                flexDirection: 'column',
                justifyContent: 'space-between',
                height: openAdvanced ? 98 : 0,
                overflow: 'hidden',
                transition: 'height 100ms linear',
            }, id: "rbgcp-advanced-controls-inner".concat(pickerIdSuffix) },
            React.createElement(AdvBar, { value: s, reffy: satRef, config: config, label: "Saturation", callback: satDesat, squareWidth: squareWidth, openAdvanced: openAdvanced, defaultStyles: defaultStyles, pickerIdSuffix: pickerIdSuffix }),
            React.createElement(AdvBar, { value: l, config: config, reffy: lightRef, label: "Lightness", callback: setLight, squareWidth: squareWidth, openAdvanced: openAdvanced, defaultStyles: defaultStyles, pickerIdSuffix: pickerIdSuffix }),
            React.createElement(AdvBar, { value: hc === null || hc === void 0 ? void 0 : hc.v, config: config, reffy: brightRef, label: "Brightness", callback: setBright, squareWidth: squareWidth, openAdvanced: openAdvanced, defaultStyles: defaultStyles, pickerIdSuffix: pickerIdSuffix }))));
};
export default AdvancedControls;
