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
import React, { useState, useEffect } from 'react';
import { formatInputValues, round } from '../utils/formatters.js';
import { rgb2cmyk, cmykToRgb, getHexAlpha } from '../utils/converters.js';
import { usePicker } from '../context.js';
import tc from 'tinycolor2';
var Input = function (_a) {
    var label = _a.label, value = _a.value, callback = _a.callback, _b = _a.max, max = _b === void 0 ? 100 : _b, hideOpacity = _a.hideOpacity, defaultStyles = _a.defaultStyles, pickerIdSuffix = _a.pickerIdSuffix;
    var _c = useState(value), temp = _c[0], setTemp = _c[1];
    var width = hideOpacity ? '25%' : '20%';
    useEffect(function () {
        setTemp(value);
    }, [value]);
    var onChange = function (e) {
        var newVal = formatInputValues(parseFloat(e.target.value), 0, max);
        setTemp(newVal);
        callback(newVal);
    };
    return (React.createElement("div", { style: { width: width, flexShrink: 1 }, id: "rbgcp-".concat(label, "-input-wrapper").concat(pickerIdSuffix) },
        React.createElement("input", { value: temp, onChange: function (e) { return onChange(e); }, style: __assign({}, defaultStyles.rbgcpInput), id: "rbgcp-".concat(label, "-input").concat(pickerIdSuffix) }),
        React.createElement("div", { style: __assign({}, defaultStyles.rbgcpInputLabel) }, label)));
};
var HexInput = function (_a) {
    var opacity = _a.opacity, tinyColor = _a.tinyColor, showHexAlpha = _a.showHexAlpha, handleChange = _a.handleChange, defaultStyles = _a.defaultStyles, pickerIdSuffix = _a.pickerIdSuffix;
    var _b = useState(''), disable = _b[0], setDisable = _b[1];
    var hex = tinyColor.toHex();
    var _c = useState(hex), newHex = _c[0], setNewHex = _c[1];
    useEffect(function () {
        if (disable !== 'hex') {
            setNewHex(hex);
        }
    }, [tinyColor, disable, hex]);
    var hexFocus = function () {
        setDisable('hex');
    };
    var hexBlur = function () {
        setDisable('');
    };
    var handleHex = function (e) {
        var tinyHex = tc(e.target.value);
        setNewHex(e.target.value);
        if (tinyHex.isValid()) {
            var _a = tinyHex.toRgb(), r = _a.r, g = _a.g, b = _a.b;
            var newColor = "rgba(".concat(r, ", ").concat(g, ", ").concat(b, ", ").concat(opacity, ")");
            handleChange(newColor);
        }
    };
    var displayValue = showHexAlpha ? "".concat(newHex).concat(getHexAlpha(opacity)) : newHex;
    var label = showHexAlpha ? 'HEXA' : 'HEX';
    var width = showHexAlpha ? 88 : 76;
    return (React.createElement("div", { style: { width: width, flexShrink: 0 }, id: "rbgcp-hex-input-wrapper".concat(pickerIdSuffix) },
        React.createElement("input", { onBlur: hexBlur, onFocus: hexFocus, onChange: function (e) { return handleHex(e); }, value: displayValue === null || displayValue === void 0 ? void 0 : displayValue.toUpperCase(), id: "rbgcp-hex-input".concat(pickerIdSuffix), style: __assign(__assign({}, defaultStyles.rbgcpInput), defaultStyles.rbgcpHexInput) }),
        React.createElement("div", { style: __assign({}, defaultStyles.rbgcpInputLabel) }, label)));
};
var RGBInputs = function (_a) {
    var hc = _a.hc, hideOpacity = _a.hideOpacity, handleChange = _a.handleChange, defaultStyles = _a.defaultStyles, pickerIdSuffix = _a.pickerIdSuffix;
    var handleRgb = function (_a) {
        var r = _a.r, g = _a.g, b = _a.b;
        handleChange("rgba(".concat(r, ", ").concat(g, ", ").concat(b, ", ").concat(hc === null || hc === void 0 ? void 0 : hc.a, ")"));
    };
    return (React.createElement(React.Fragment, null,
        React.createElement(Input, { label: "R", max: 255, value: hc === null || hc === void 0 ? void 0 : hc.r, hideOpacity: hideOpacity, defaultStyles: defaultStyles, pickerIdSuffix: pickerIdSuffix, callback: function (newVal) { return handleRgb({ r: newVal, g: hc === null || hc === void 0 ? void 0 : hc.g, b: hc === null || hc === void 0 ? void 0 : hc.b }); } }),
        React.createElement(Input, { label: "G", max: 255, value: hc === null || hc === void 0 ? void 0 : hc.g, hideOpacity: hideOpacity, defaultStyles: defaultStyles, pickerIdSuffix: pickerIdSuffix, callback: function (newVal) { return handleRgb({ r: hc === null || hc === void 0 ? void 0 : hc.r, g: newVal, b: hc === null || hc === void 0 ? void 0 : hc.b }); } }),
        React.createElement(Input, { label: "B", max: 255, value: hc === null || hc === void 0 ? void 0 : hc.b, hideOpacity: hideOpacity, defaultStyles: defaultStyles, pickerIdSuffix: pickerIdSuffix, callback: function (newVal) { return handleRgb({ r: hc === null || hc === void 0 ? void 0 : hc.r, g: hc === null || hc === void 0 ? void 0 : hc.g, b: newVal }); } })));
};
var HSLInputs = function (_a) {
    var hc = _a.hc, setHc = _a.setHc, tinyColor = _a.tinyColor, hideOpacity = _a.hideOpacity, handleChange = _a.handleChange, defaultStyles = _a.defaultStyles, pickerIdSuffix = _a.pickerIdSuffix;
    var _b = tinyColor.toHsl(), s = _b.s, l = _b.l;
    var handleH = function (h, s, l) {
        var _a = tc({ h: h, s: s, l: l }).toRgb(), r = _a.r, g = _a.g, b = _a.b;
        handleChange("rgba(".concat(r, ", ").concat(g, ", ").concat(b, ", ").concat(hc === null || hc === void 0 ? void 0 : hc.a, ")"));
        setHc(__assign(__assign({}, hc), { h: h }));
    };
    var handleSl = function (value) {
        var _a = tc(value).toRgb(), r = _a.r, g = _a.g, b = _a.b;
        handleChange("rgba(".concat(r, ", ").concat(g, ", ").concat(b, ", ").concat(hc === null || hc === void 0 ? void 0 : hc.a, ")"));
    };
    return (React.createElement(React.Fragment, null,
        React.createElement(Input, { label: "H", max: 360, value: round(hc === null || hc === void 0 ? void 0 : hc.h), hideOpacity: hideOpacity, defaultStyles: defaultStyles, pickerIdSuffix: pickerIdSuffix, callback: function (newVal) { return handleH(newVal, s, l); } }),
        React.createElement(Input, { label: "S", value: round(s * 100), hideOpacity: hideOpacity, defaultStyles: defaultStyles, pickerIdSuffix: pickerIdSuffix, callback: function (newVal) { return handleSl({ h: hc === null || hc === void 0 ? void 0 : hc.h, s: newVal, l: l }); } }),
        React.createElement(Input, { label: "L", value: round(l * 100), hideOpacity: hideOpacity, defaultStyles: defaultStyles, pickerIdSuffix: pickerIdSuffix, callback: function (newVal) { return handleSl({ h: hc === null || hc === void 0 ? void 0 : hc.h, s: s, l: newVal }); } })));
};
var HSVInputs = function (_a) {
    var hc = _a.hc, setHc = _a.setHc, hideOpacity = _a.hideOpacity, handleChange = _a.handleChange, defaultStyles = _a.defaultStyles, pickerIdSuffix = _a.pickerIdSuffix;
    var handleH = function (h, s, v) {
        var _a = tc({ h: h, s: s, v: v }).toRgb(), r = _a.r, g = _a.g, b = _a.b;
        handleChange("rgba(".concat(r, ", ").concat(g, ", ").concat(b, ", ").concat(hc === null || hc === void 0 ? void 0 : hc.a, ")"));
        setHc(__assign(__assign({}, hc), { h: h }));
    };
    var handleSV = function (value) {
        var _a = tc(value).toRgb(), r = _a.r, g = _a.g, b = _a.b;
        handleChange("rgba(".concat(r, ", ").concat(g, ", ").concat(b, ", ").concat(hc === null || hc === void 0 ? void 0 : hc.a, ")"));
    };
    return (React.createElement(React.Fragment, null,
        React.createElement(Input, { label: "H", max: 360, value: round(hc === null || hc === void 0 ? void 0 : hc.h), hideOpacity: hideOpacity, defaultStyles: defaultStyles, pickerIdSuffix: pickerIdSuffix, callback: function (newVal) { return handleH(newVal, hc === null || hc === void 0 ? void 0 : hc.s, hc === null || hc === void 0 ? void 0 : hc.v); } }),
        React.createElement(Input, { label: "S", hideOpacity: hideOpacity, value: round((hc === null || hc === void 0 ? void 0 : hc.s) * 100), defaultStyles: defaultStyles, pickerIdSuffix: pickerIdSuffix, callback: function (newVal) { return handleSV({ h: hc === null || hc === void 0 ? void 0 : hc.h, s: newVal, v: hc === null || hc === void 0 ? void 0 : hc.v }); } }),
        React.createElement(Input, { label: "V", hideOpacity: hideOpacity, value: round((hc === null || hc === void 0 ? void 0 : hc.v) * 100), defaultStyles: defaultStyles, pickerIdSuffix: pickerIdSuffix, callback: function (newVal) { return handleSV({ h: hc === null || hc === void 0 ? void 0 : hc.h, s: hc === null || hc === void 0 ? void 0 : hc.s, v: newVal }); } })));
};
var CMKYInputs = function (_a) {
    var hc = _a.hc, hideOpacity = _a.hideOpacity, handleChange = _a.handleChange, defaultStyles = _a.defaultStyles, pickerIdSuffix = _a.pickerIdSuffix;
    var _b = rgb2cmyk(hc === null || hc === void 0 ? void 0 : hc.r, hc === null || hc === void 0 ? void 0 : hc.g, hc === null || hc === void 0 ? void 0 : hc.b), c = _b.c, m = _b.m, y = _b.y, k = _b.k;
    var handleCmyk = function (value) {
        var _a = cmykToRgb(value), r = _a.r, g = _a.g, b = _a.b;
        handleChange("rgba(".concat(r, ", ").concat(g, ", ").concat(b, ", ").concat(hc === null || hc === void 0 ? void 0 : hc.a, ")"));
    };
    return (React.createElement(React.Fragment, null,
        React.createElement(Input, { label: "C", value: round(c * 100), hideOpacity: hideOpacity, defaultStyles: defaultStyles, pickerIdSuffix: pickerIdSuffix, callback: function (newVal) { return handleCmyk({ c: newVal / 100, m: m, y: y, k: k }); } }),
        React.createElement(Input, { label: "M", value: round(m * 100), hideOpacity: hideOpacity, defaultStyles: defaultStyles, pickerIdSuffix: pickerIdSuffix, callback: function (newVal) { return handleCmyk({ c: c, m: newVal / 100, y: y, k: k }); } }),
        React.createElement(Input, { label: "Y", value: round(y * 100), hideOpacity: hideOpacity, defaultStyles: defaultStyles, pickerIdSuffix: pickerIdSuffix, callback: function (newVal) { return handleCmyk({ c: c, m: m, y: newVal / 100, k: k }); } }),
        React.createElement(Input, { label: "K", value: round(k * 100), hideOpacity: hideOpacity, defaultStyles: defaultStyles, pickerIdSuffix: pickerIdSuffix, callback: function (newVal) { return handleCmyk({ c: c, m: m, y: y, k: newVal / 100 }); } })));
};
var Inputs = function () {
    var _a = usePicker(), hc = _a.hc, setHc = _a.setHc, inputType = _a.inputType, tinyColor = _a.tinyColor, hideOpacity = _a.hideOpacity, showHexAlpha = _a.showHexAlpha, handleChange = _a.handleChange, defaultStyles = _a.defaultStyles, pickerIdSuffix = _a.pickerIdSuffix;
    return (React.createElement("div", { style: __assign({ columnGap: 6, paddingTop: 14, display: 'flex', justifyContent: 'space-between' }, defaultStyles.rbgcpInputsWrap), id: "rbgcp-inputs-wrap".concat(pickerIdSuffix) },
        inputType !== 'cmyk' && (React.createElement(HexInput, { opacity: hc === null || hc === void 0 ? void 0 : hc.a, tinyColor: tinyColor, showHexAlpha: showHexAlpha, handleChange: handleChange, defaultStyles: defaultStyles, pickerIdSuffix: pickerIdSuffix })),
        inputType === 'hsl' && (React.createElement(HSLInputs, { hc: hc, setHc: setHc, tinyColor: tinyColor, hideOpacity: hideOpacity, handleChange: handleChange, defaultStyles: defaultStyles, pickerIdSuffix: pickerIdSuffix })),
        inputType === 'rgb' && (React.createElement(RGBInputs, { hc: hc, hideOpacity: hideOpacity, handleChange: handleChange, defaultStyles: defaultStyles, pickerIdSuffix: pickerIdSuffix })),
        inputType === 'hsv' && (React.createElement(HSVInputs, { hc: hc, setHc: setHc, hideOpacity: hideOpacity, handleChange: handleChange, defaultStyles: defaultStyles, pickerIdSuffix: pickerIdSuffix })),
        inputType === 'cmyk' && (React.createElement(CMKYInputs, { hc: hc, hideOpacity: hideOpacity, handleChange: handleChange, defaultStyles: defaultStyles, pickerIdSuffix: pickerIdSuffix })),
        !hideOpacity && (React.createElement(Input, { label: "A", hideOpacity: hideOpacity, defaultStyles: defaultStyles, value: Math.round((hc === null || hc === void 0 ? void 0 : hc.a) * 100), pickerIdSuffix: pickerIdSuffix, callback: function (newVal) {
                return handleChange("rgba(".concat(hc === null || hc === void 0 ? void 0 : hc.r, ", ").concat(hc === null || hc === void 0 ? void 0 : hc.g, ", ").concat(hc === null || hc === void 0 ? void 0 : hc.b, ", ").concat(newVal / 100, ")"));
            } }))));
};
export default Inputs;
