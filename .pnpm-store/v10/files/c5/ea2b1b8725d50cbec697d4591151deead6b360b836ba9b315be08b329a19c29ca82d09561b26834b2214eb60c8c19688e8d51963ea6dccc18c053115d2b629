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
var formatters_js_1 = require("../utils/formatters.js");
var converters_js_1 = require("../utils/converters.js");
var context_js_1 = require("../context.js");
var tinycolor2_1 = __importDefault(require("tinycolor2"));
var Input = function (_a) {
    var label = _a.label, value = _a.value, callback = _a.callback, _b = _a.max, max = _b === void 0 ? 100 : _b, hideOpacity = _a.hideOpacity, defaultStyles = _a.defaultStyles, pickerIdSuffix = _a.pickerIdSuffix;
    var _c = (0, react_1.useState)(value), temp = _c[0], setTemp = _c[1];
    var width = hideOpacity ? '25%' : '20%';
    (0, react_1.useEffect)(function () {
        setTemp(value);
    }, [value]);
    var onChange = function (e) {
        var newVal = (0, formatters_js_1.formatInputValues)(parseFloat(e.target.value), 0, max);
        setTemp(newVal);
        callback(newVal);
    };
    return (react_1.default.createElement("div", { style: { width: width, flexShrink: 1 }, id: "rbgcp-".concat(label, "-input-wrapper").concat(pickerIdSuffix) },
        react_1.default.createElement("input", { value: temp, onChange: function (e) { return onChange(e); }, style: __assign({}, defaultStyles.rbgcpInput), id: "rbgcp-".concat(label, "-input").concat(pickerIdSuffix) }),
        react_1.default.createElement("div", { style: __assign({}, defaultStyles.rbgcpInputLabel) }, label)));
};
var HexInput = function (_a) {
    var opacity = _a.opacity, tinyColor = _a.tinyColor, showHexAlpha = _a.showHexAlpha, handleChange = _a.handleChange, defaultStyles = _a.defaultStyles, pickerIdSuffix = _a.pickerIdSuffix;
    var _b = (0, react_1.useState)(''), disable = _b[0], setDisable = _b[1];
    var hex = tinyColor.toHex();
    var _c = (0, react_1.useState)(hex), newHex = _c[0], setNewHex = _c[1];
    (0, react_1.useEffect)(function () {
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
        var tinyHex = (0, tinycolor2_1.default)(e.target.value);
        setNewHex(e.target.value);
        if (tinyHex.isValid()) {
            var _a = tinyHex.toRgb(), r = _a.r, g = _a.g, b = _a.b;
            var newColor = "rgba(".concat(r, ", ").concat(g, ", ").concat(b, ", ").concat(opacity, ")");
            handleChange(newColor);
        }
    };
    var displayValue = showHexAlpha ? "".concat(newHex).concat((0, converters_js_1.getHexAlpha)(opacity)) : newHex;
    var label = showHexAlpha ? 'HEXA' : 'HEX';
    var width = showHexAlpha ? 88 : 76;
    return (react_1.default.createElement("div", { style: { width: width, flexShrink: 0 }, id: "rbgcp-hex-input-wrapper".concat(pickerIdSuffix) },
        react_1.default.createElement("input", { onBlur: hexBlur, onFocus: hexFocus, onChange: function (e) { return handleHex(e); }, value: displayValue === null || displayValue === void 0 ? void 0 : displayValue.toUpperCase(), id: "rbgcp-hex-input".concat(pickerIdSuffix), style: __assign(__assign({}, defaultStyles.rbgcpInput), defaultStyles.rbgcpHexInput) }),
        react_1.default.createElement("div", { style: __assign({}, defaultStyles.rbgcpInputLabel) }, label)));
};
var RGBInputs = function (_a) {
    var hc = _a.hc, hideOpacity = _a.hideOpacity, handleChange = _a.handleChange, defaultStyles = _a.defaultStyles, pickerIdSuffix = _a.pickerIdSuffix;
    var handleRgb = function (_a) {
        var r = _a.r, g = _a.g, b = _a.b;
        handleChange("rgba(".concat(r, ", ").concat(g, ", ").concat(b, ", ").concat(hc === null || hc === void 0 ? void 0 : hc.a, ")"));
    };
    return (react_1.default.createElement(react_1.default.Fragment, null,
        react_1.default.createElement(Input, { label: "R", max: 255, value: hc === null || hc === void 0 ? void 0 : hc.r, hideOpacity: hideOpacity, defaultStyles: defaultStyles, pickerIdSuffix: pickerIdSuffix, callback: function (newVal) { return handleRgb({ r: newVal, g: hc === null || hc === void 0 ? void 0 : hc.g, b: hc === null || hc === void 0 ? void 0 : hc.b }); } }),
        react_1.default.createElement(Input, { label: "G", max: 255, value: hc === null || hc === void 0 ? void 0 : hc.g, hideOpacity: hideOpacity, defaultStyles: defaultStyles, pickerIdSuffix: pickerIdSuffix, callback: function (newVal) { return handleRgb({ r: hc === null || hc === void 0 ? void 0 : hc.r, g: newVal, b: hc === null || hc === void 0 ? void 0 : hc.b }); } }),
        react_1.default.createElement(Input, { label: "B", max: 255, value: hc === null || hc === void 0 ? void 0 : hc.b, hideOpacity: hideOpacity, defaultStyles: defaultStyles, pickerIdSuffix: pickerIdSuffix, callback: function (newVal) { return handleRgb({ r: hc === null || hc === void 0 ? void 0 : hc.r, g: hc === null || hc === void 0 ? void 0 : hc.g, b: newVal }); } })));
};
var HSLInputs = function (_a) {
    var hc = _a.hc, setHc = _a.setHc, tinyColor = _a.tinyColor, hideOpacity = _a.hideOpacity, handleChange = _a.handleChange, defaultStyles = _a.defaultStyles, pickerIdSuffix = _a.pickerIdSuffix;
    var _b = tinyColor.toHsl(), s = _b.s, l = _b.l;
    var handleH = function (h, s, l) {
        var _a = (0, tinycolor2_1.default)({ h: h, s: s, l: l }).toRgb(), r = _a.r, g = _a.g, b = _a.b;
        handleChange("rgba(".concat(r, ", ").concat(g, ", ").concat(b, ", ").concat(hc === null || hc === void 0 ? void 0 : hc.a, ")"));
        setHc(__assign(__assign({}, hc), { h: h }));
    };
    var handleSl = function (value) {
        var _a = (0, tinycolor2_1.default)(value).toRgb(), r = _a.r, g = _a.g, b = _a.b;
        handleChange("rgba(".concat(r, ", ").concat(g, ", ").concat(b, ", ").concat(hc === null || hc === void 0 ? void 0 : hc.a, ")"));
    };
    return (react_1.default.createElement(react_1.default.Fragment, null,
        react_1.default.createElement(Input, { label: "H", max: 360, value: (0, formatters_js_1.round)(hc === null || hc === void 0 ? void 0 : hc.h), hideOpacity: hideOpacity, defaultStyles: defaultStyles, pickerIdSuffix: pickerIdSuffix, callback: function (newVal) { return handleH(newVal, s, l); } }),
        react_1.default.createElement(Input, { label: "S", value: (0, formatters_js_1.round)(s * 100), hideOpacity: hideOpacity, defaultStyles: defaultStyles, pickerIdSuffix: pickerIdSuffix, callback: function (newVal) { return handleSl({ h: hc === null || hc === void 0 ? void 0 : hc.h, s: newVal, l: l }); } }),
        react_1.default.createElement(Input, { label: "L", value: (0, formatters_js_1.round)(l * 100), hideOpacity: hideOpacity, defaultStyles: defaultStyles, pickerIdSuffix: pickerIdSuffix, callback: function (newVal) { return handleSl({ h: hc === null || hc === void 0 ? void 0 : hc.h, s: s, l: newVal }); } })));
};
var HSVInputs = function (_a) {
    var hc = _a.hc, setHc = _a.setHc, hideOpacity = _a.hideOpacity, handleChange = _a.handleChange, defaultStyles = _a.defaultStyles, pickerIdSuffix = _a.pickerIdSuffix;
    var handleH = function (h, s, v) {
        var _a = (0, tinycolor2_1.default)({ h: h, s: s, v: v }).toRgb(), r = _a.r, g = _a.g, b = _a.b;
        handleChange("rgba(".concat(r, ", ").concat(g, ", ").concat(b, ", ").concat(hc === null || hc === void 0 ? void 0 : hc.a, ")"));
        setHc(__assign(__assign({}, hc), { h: h }));
    };
    var handleSV = function (value) {
        var _a = (0, tinycolor2_1.default)(value).toRgb(), r = _a.r, g = _a.g, b = _a.b;
        handleChange("rgba(".concat(r, ", ").concat(g, ", ").concat(b, ", ").concat(hc === null || hc === void 0 ? void 0 : hc.a, ")"));
    };
    return (react_1.default.createElement(react_1.default.Fragment, null,
        react_1.default.createElement(Input, { label: "H", max: 360, value: (0, formatters_js_1.round)(hc === null || hc === void 0 ? void 0 : hc.h), hideOpacity: hideOpacity, defaultStyles: defaultStyles, pickerIdSuffix: pickerIdSuffix, callback: function (newVal) { return handleH(newVal, hc === null || hc === void 0 ? void 0 : hc.s, hc === null || hc === void 0 ? void 0 : hc.v); } }),
        react_1.default.createElement(Input, { label: "S", hideOpacity: hideOpacity, value: (0, formatters_js_1.round)((hc === null || hc === void 0 ? void 0 : hc.s) * 100), defaultStyles: defaultStyles, pickerIdSuffix: pickerIdSuffix, callback: function (newVal) { return handleSV({ h: hc === null || hc === void 0 ? void 0 : hc.h, s: newVal, v: hc === null || hc === void 0 ? void 0 : hc.v }); } }),
        react_1.default.createElement(Input, { label: "V", hideOpacity: hideOpacity, value: (0, formatters_js_1.round)((hc === null || hc === void 0 ? void 0 : hc.v) * 100), defaultStyles: defaultStyles, pickerIdSuffix: pickerIdSuffix, callback: function (newVal) { return handleSV({ h: hc === null || hc === void 0 ? void 0 : hc.h, s: hc === null || hc === void 0 ? void 0 : hc.s, v: newVal }); } })));
};
var CMKYInputs = function (_a) {
    var hc = _a.hc, hideOpacity = _a.hideOpacity, handleChange = _a.handleChange, defaultStyles = _a.defaultStyles, pickerIdSuffix = _a.pickerIdSuffix;
    var _b = (0, converters_js_1.rgb2cmyk)(hc === null || hc === void 0 ? void 0 : hc.r, hc === null || hc === void 0 ? void 0 : hc.g, hc === null || hc === void 0 ? void 0 : hc.b), c = _b.c, m = _b.m, y = _b.y, k = _b.k;
    var handleCmyk = function (value) {
        var _a = (0, converters_js_1.cmykToRgb)(value), r = _a.r, g = _a.g, b = _a.b;
        handleChange("rgba(".concat(r, ", ").concat(g, ", ").concat(b, ", ").concat(hc === null || hc === void 0 ? void 0 : hc.a, ")"));
    };
    return (react_1.default.createElement(react_1.default.Fragment, null,
        react_1.default.createElement(Input, { label: "C", value: (0, formatters_js_1.round)(c * 100), hideOpacity: hideOpacity, defaultStyles: defaultStyles, pickerIdSuffix: pickerIdSuffix, callback: function (newVal) { return handleCmyk({ c: newVal / 100, m: m, y: y, k: k }); } }),
        react_1.default.createElement(Input, { label: "M", value: (0, formatters_js_1.round)(m * 100), hideOpacity: hideOpacity, defaultStyles: defaultStyles, pickerIdSuffix: pickerIdSuffix, callback: function (newVal) { return handleCmyk({ c: c, m: newVal / 100, y: y, k: k }); } }),
        react_1.default.createElement(Input, { label: "Y", value: (0, formatters_js_1.round)(y * 100), hideOpacity: hideOpacity, defaultStyles: defaultStyles, pickerIdSuffix: pickerIdSuffix, callback: function (newVal) { return handleCmyk({ c: c, m: m, y: newVal / 100, k: k }); } }),
        react_1.default.createElement(Input, { label: "K", value: (0, formatters_js_1.round)(k * 100), hideOpacity: hideOpacity, defaultStyles: defaultStyles, pickerIdSuffix: pickerIdSuffix, callback: function (newVal) { return handleCmyk({ c: c, m: m, y: y, k: newVal / 100 }); } })));
};
var Inputs = function () {
    var _a = (0, context_js_1.usePicker)(), hc = _a.hc, setHc = _a.setHc, inputType = _a.inputType, tinyColor = _a.tinyColor, hideOpacity = _a.hideOpacity, showHexAlpha = _a.showHexAlpha, handleChange = _a.handleChange, defaultStyles = _a.defaultStyles, pickerIdSuffix = _a.pickerIdSuffix;
    return (react_1.default.createElement("div", { style: __assign({ columnGap: 6, paddingTop: 14, display: 'flex', justifyContent: 'space-between' }, defaultStyles.rbgcpInputsWrap), id: "rbgcp-inputs-wrap".concat(pickerIdSuffix) },
        inputType !== 'cmyk' && (react_1.default.createElement(HexInput, { opacity: hc === null || hc === void 0 ? void 0 : hc.a, tinyColor: tinyColor, showHexAlpha: showHexAlpha, handleChange: handleChange, defaultStyles: defaultStyles, pickerIdSuffix: pickerIdSuffix })),
        inputType === 'hsl' && (react_1.default.createElement(HSLInputs, { hc: hc, setHc: setHc, tinyColor: tinyColor, hideOpacity: hideOpacity, handleChange: handleChange, defaultStyles: defaultStyles, pickerIdSuffix: pickerIdSuffix })),
        inputType === 'rgb' && (react_1.default.createElement(RGBInputs, { hc: hc, hideOpacity: hideOpacity, handleChange: handleChange, defaultStyles: defaultStyles, pickerIdSuffix: pickerIdSuffix })),
        inputType === 'hsv' && (react_1.default.createElement(HSVInputs, { hc: hc, setHc: setHc, hideOpacity: hideOpacity, handleChange: handleChange, defaultStyles: defaultStyles, pickerIdSuffix: pickerIdSuffix })),
        inputType === 'cmyk' && (react_1.default.createElement(CMKYInputs, { hc: hc, hideOpacity: hideOpacity, handleChange: handleChange, defaultStyles: defaultStyles, pickerIdSuffix: pickerIdSuffix })),
        !hideOpacity && (react_1.default.createElement(Input, { label: "A", hideOpacity: hideOpacity, defaultStyles: defaultStyles, value: Math.round((hc === null || hc === void 0 ? void 0 : hc.a) * 100), pickerIdSuffix: pickerIdSuffix, callback: function (newVal) {
                return handleChange("rgba(".concat(hc === null || hc === void 0 ? void 0 : hc.r, ", ").concat(hc === null || hc === void 0 ? void 0 : hc.g, ", ").concat(hc === null || hc === void 0 ? void 0 : hc.b, ", ").concat(newVal / 100, ")"));
            } }))));
};
exports.default = Inputs;
