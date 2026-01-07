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
var icon_js_1 = require("./icon.js");
var context_js_1 = require("../context.js");
var EyeDropper_js_1 = __importDefault(require("./EyeDropper.js"));
var AdvancedControls_js_1 = __importDefault(require("./AdvancedControls.js"));
var ComparibleColors_js_1 = __importDefault(require("./ComparibleColors.js"));
var GradientControls_js_1 = __importDefault(require("./GradientControls.js"));
var styles_js_1 = require("../styles/styles.js");
var ColorTypeBtns = function (_a) {
    var _b, _c;
    var hideColorTypeBtns = _a.hideColorTypeBtns, setGradient = _a.setGradient, isGradient = _a.isGradient, setSolid = _a.setSolid, locales = _a.locales;
    var _d = (0, context_js_1.usePicker)(), defaultStyles = _d.defaultStyles, pickerIdSuffix = _d.pickerIdSuffix;
    if (hideColorTypeBtns) {
        return react_1.default.createElement("div", { style: { width: 1 } });
    }
    else {
        return (react_1.default.createElement("div", { style: __assign({ display: 'flex', alignItems: 'center' }, defaultStyles.rbgcpControlBtnWrapper), id: "rbgcp-color-type-btns".concat(pickerIdSuffix) },
            react_1.default.createElement("div", { onClick: setSolid, id: "rbgcp-solid-btn".concat(pickerIdSuffix), style: (0, styles_js_1.colorTypeBtnStyles)(!isGradient, defaultStyles) }, (_b = locales === null || locales === void 0 ? void 0 : locales.CONTROLS) === null || _b === void 0 ? void 0 : _b.SOLID),
            react_1.default.createElement("div", { onClick: setGradient, id: "rbgcp-gradient-btn".concat(pickerIdSuffix), style: (0, styles_js_1.colorTypeBtnStyles)(isGradient !== null && isGradient !== void 0 ? isGradient : false, defaultStyles) }, (_c = locales === null || locales === void 0 ? void 0 : locales.CONTROLS) === null || _c === void 0 ? void 0 : _c.GRADIENT)));
    }
};
var InputTypeDropdown = function (_a) {
    var openInputType = _a.openInputType, setOpenInputType = _a.setOpenInputType;
    var _b = (0, context_js_1.usePicker)(), inputType = _b.inputType, setInputType = _b.setInputType, defaultStyles = _b.defaultStyles, pickerIdSuffix = _b.pickerIdSuffix;
    var vTrans = openInputType
        ? 'visibility 0ms linear'
        : 'visibility 100ms linear 150ms';
    var zTrans = openInputType
        ? 'z-index 0ms linear'
        : 'z-index 100ms linear 150ms';
    var oTrans = openInputType
        ? 'opacity 120ms linear'
        : 'opacity 150ms linear 50ms';
    var handleInputType = function (e, val) {
        if (openInputType) {
            e.stopPropagation();
            setInputType(val);
            setOpenInputType(false);
        }
    };
    return (react_1.default.createElement("div", { 
        // className="rbgcp-color-model-dropdown"
        style: __assign({ visibility: openInputType ? 'visible' : 'hidden', zIndex: openInputType ? '' : -100, opacity: openInputType ? 1 : 0, transition: "".concat(oTrans, ", ").concat(vTrans, ", ").concat(zTrans) }, defaultStyles.rbgcpColorModelDropdown), id: "rbgcp-color-model-dropdown".concat(pickerIdSuffix) },
        react_1.default.createElement("div", { id: "rbgcp-color-model-rgb-btn".concat(pickerIdSuffix), onClick: function (e) { return handleInputType(e, 'rgb'); }, style: (0, styles_js_1.modalBtnStyles)(inputType === 'rgb', defaultStyles) }, "RGB"),
        react_1.default.createElement("div", { id: "rbgcp-color-model-hsl-btn".concat(pickerIdSuffix), onClick: function (e) { return handleInputType(e, 'hsl'); }, style: (0, styles_js_1.modalBtnStyles)(inputType === 'hsl', defaultStyles) }, "HSL"),
        react_1.default.createElement("div", { id: "rbgcp-color-model-hsv-btn".concat(pickerIdSuffix), onClick: function (e) { return handleInputType(e, 'hsv'); }, style: (0, styles_js_1.modalBtnStyles)(inputType === 'hsv', defaultStyles) }, "HSV"),
        react_1.default.createElement("div", { id: "rbgcp-color-model-cmyk-btn".concat(pickerIdSuffix), onClick: function (e) { return handleInputType(e, 'cmyk'); }, style: (0, styles_js_1.modalBtnStyles)(inputType === 'cmyk', defaultStyles) }, "CMYK")));
};
var Controls = function (_a) {
    var _b, _c;
    var locales = _a.locales, _d = _a.hideEyeDrop, hideEyeDrop = _d === void 0 ? false : _d, _e = _a.hideAdvancedSliders, hideAdvancedSliders = _e === void 0 ? false : _e, _f = _a.hideColorGuide, hideColorGuide = _f === void 0 ? false : _f, _g = _a.hideInputType, hideInputType = _g === void 0 ? false : _g, _h = _a.hideColorTypeBtns, hideColorTypeBtns = _h === void 0 ? false : _h, _j = _a.hideGradientControls, hideGradientControls = _j === void 0 ? false : _j, _k = _a.hideGradientType, hideGradientType = _k === void 0 ? false : _k, _l = _a.hideGradientAngle, hideGradientAngle = _l === void 0 ? false : _l, _m = _a.hideGradientStop, hideGradientStop = _m === void 0 ? false : _m;
    var _o = (0, context_js_1.usePicker)(), config = _o.config, onChange = _o.onChange, isGradient = _o.isGradient, handleChange = _o.handleChange, previous = _o.previous, defaultStyles = _o.defaultStyles, pickerIdSuffix = _o.pickerIdSuffix;
    var defaultColor = config.defaultColor, defaultGradient = config.defaultGradient;
    var _p = (0, react_1.useState)(false), openComparibles = _p[0], setOpenComparibles = _p[1];
    var _q = (0, react_1.useState)(false), openInputType = _q[0], setOpenInputType = _q[1];
    var _r = (0, react_1.useState)(false), openAdvanced = _r[0], setOpenAdvanced = _r[1];
    var noTools = hideEyeDrop && hideAdvancedSliders && hideColorGuide && hideInputType;
    var solidColor = (_b = previous === null || previous === void 0 ? void 0 : previous.color) !== null && _b !== void 0 ? _b : defaultColor;
    var gradientColor = (_c = previous === null || previous === void 0 ? void 0 : previous.gradient) !== null && _c !== void 0 ? _c : defaultGradient;
    var setSolid = function () {
        onChange(solidColor);
    };
    var setGradient = function () {
        onChange(gradientColor);
    };
    var allRightControlsHidden = hideEyeDrop && hideAdvancedSliders && hideColorGuide && hideInputType;
    var allControlsHidden = allRightControlsHidden && hideColorTypeBtns;
    if (allControlsHidden) {
        if (isGradient && !hideGradientControls) {
            return (react_1.default.createElement(GradientControls_js_1.default, { hideGradientType: hideGradientType, hideGradientAngle: hideGradientAngle, hideGradientStop: hideGradientStop }));
        }
        else {
            return null;
        }
    }
    else {
        return (react_1.default.createElement("div", { style: { paddingBottom: 4 } },
            react_1.default.createElement("div", { style: {
                    width: '100%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                }, id: "rbgcp-controls-wrapper".concat(pickerIdSuffix) },
                react_1.default.createElement(ColorTypeBtns, { hideColorTypeBtns: hideColorTypeBtns, setGradient: setGradient, isGradient: isGradient, setSolid: setSolid, locales: locales }),
                !allRightControlsHidden && (react_1.default.createElement("div", { style: __assign({ display: noTools ? 'none' : '' }, defaultStyles.rbgcpControlBtnWrapper), id: "rbgcp-control-rightside-wrapper".concat(pickerIdSuffix) },
                    !hideEyeDrop && react_1.default.createElement(EyeDropper_js_1.default, { onSelect: handleChange }),
                    !hideAdvancedSliders && (react_1.default.createElement("div", { id: "rbgcp-advanced-btn".concat(pickerIdSuffix), onClick: function () { return setOpenAdvanced(!openAdvanced); }, 
                        // className="rbgcp-control-btn rbgcp-advanced-btn"
                        style: (0, styles_js_1.controlBtnStyles)(openAdvanced, defaultStyles) },
                        react_1.default.createElement(icon_js_1.SlidersIcon, { color: openAdvanced ? '#568CF5' : '' }))),
                    !hideColorGuide && (react_1.default.createElement("div", { style: (0, styles_js_1.controlBtnStyles)(openComparibles, defaultStyles), onClick: function () { return setOpenComparibles(!openComparibles); }, 
                        // className="rbgcp-control-btn rbgcp-comparibles-btn"
                        id: "rbgcp-comparibles-btn".concat(pickerIdSuffix) },
                        react_1.default.createElement(icon_js_1.PaletteIcon, { color: openComparibles ? '#568CF5' : '' }))),
                    !hideInputType && (react_1.default.createElement("div", { id: "rbgcp-color-model-btn".concat(pickerIdSuffix), onClick: function () { return setOpenInputType(!openInputType); }, 
                        // className="rbgcp-control-btn rbgcp-color-model-btn"
                        style: (0, styles_js_1.controlBtnStyles)(openInputType, defaultStyles) },
                        react_1.default.createElement(icon_js_1.InputsIcon, { color: openInputType ? '#568CF5' : '' }),
                        react_1.default.createElement(InputTypeDropdown, { openInputType: openInputType, setOpenInputType: setOpenInputType })))))),
            !hideAdvancedSliders && (react_1.default.createElement(AdvancedControls_js_1.default, { openAdvanced: openAdvanced })),
            !hideColorGuide && (react_1.default.createElement(ComparibleColors_js_1.default, { openComparibles: openComparibles })),
            isGradient && !hideGradientControls && (react_1.default.createElement(GradientControls_js_1.default, { hideGradientType: hideGradientType, hideGradientAngle: hideGradientAngle, hideGradientStop: hideGradientStop }))));
    }
};
exports.default = Controls;
