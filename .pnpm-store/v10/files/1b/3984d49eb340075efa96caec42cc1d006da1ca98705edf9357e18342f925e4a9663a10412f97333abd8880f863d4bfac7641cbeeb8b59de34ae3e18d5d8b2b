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
/* eslint-disable react/jsx-no-leaked-render */
/* eslint-disable jsx-a11y/no-static-element-interactions */
import React, { useState } from 'react';
import { SlidersIcon, InputsIcon, PaletteIcon } from './icon.js';
import { usePicker } from '../context.js';
import EyeDropper from './EyeDropper.js';
import AdvancedControls from './AdvancedControls.js';
import ComparibleColors from './ComparibleColors.js';
import GradientControls from './GradientControls.js';
import { colorTypeBtnStyles, controlBtnStyles, modalBtnStyles } from '../styles/styles.js';
var ColorTypeBtns = function (_a) {
    var _b, _c;
    var hideColorTypeBtns = _a.hideColorTypeBtns, setGradient = _a.setGradient, isGradient = _a.isGradient, setSolid = _a.setSolid, locales = _a.locales;
    var _d = usePicker(), defaultStyles = _d.defaultStyles, pickerIdSuffix = _d.pickerIdSuffix;
    if (hideColorTypeBtns) {
        return React.createElement("div", { style: { width: 1 } });
    }
    else {
        return (React.createElement("div", { style: __assign({ display: 'flex', alignItems: 'center' }, defaultStyles.rbgcpControlBtnWrapper), id: "rbgcp-color-type-btns".concat(pickerIdSuffix) },
            React.createElement("div", { onClick: setSolid, id: "rbgcp-solid-btn".concat(pickerIdSuffix), style: colorTypeBtnStyles(!isGradient, defaultStyles) }, (_b = locales === null || locales === void 0 ? void 0 : locales.CONTROLS) === null || _b === void 0 ? void 0 : _b.SOLID),
            React.createElement("div", { onClick: setGradient, id: "rbgcp-gradient-btn".concat(pickerIdSuffix), style: colorTypeBtnStyles(isGradient !== null && isGradient !== void 0 ? isGradient : false, defaultStyles) }, (_c = locales === null || locales === void 0 ? void 0 : locales.CONTROLS) === null || _c === void 0 ? void 0 : _c.GRADIENT)));
    }
};
var InputTypeDropdown = function (_a) {
    var openInputType = _a.openInputType, setOpenInputType = _a.setOpenInputType;
    var _b = usePicker(), inputType = _b.inputType, setInputType = _b.setInputType, defaultStyles = _b.defaultStyles, pickerIdSuffix = _b.pickerIdSuffix;
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
    return (React.createElement("div", { 
        // className="rbgcp-color-model-dropdown"
        style: __assign({ visibility: openInputType ? 'visible' : 'hidden', zIndex: openInputType ? '' : -100, opacity: openInputType ? 1 : 0, transition: "".concat(oTrans, ", ").concat(vTrans, ", ").concat(zTrans) }, defaultStyles.rbgcpColorModelDropdown), id: "rbgcp-color-model-dropdown".concat(pickerIdSuffix) },
        React.createElement("div", { id: "rbgcp-color-model-rgb-btn".concat(pickerIdSuffix), onClick: function (e) { return handleInputType(e, 'rgb'); }, style: modalBtnStyles(inputType === 'rgb', defaultStyles) }, "RGB"),
        React.createElement("div", { id: "rbgcp-color-model-hsl-btn".concat(pickerIdSuffix), onClick: function (e) { return handleInputType(e, 'hsl'); }, style: modalBtnStyles(inputType === 'hsl', defaultStyles) }, "HSL"),
        React.createElement("div", { id: "rbgcp-color-model-hsv-btn".concat(pickerIdSuffix), onClick: function (e) { return handleInputType(e, 'hsv'); }, style: modalBtnStyles(inputType === 'hsv', defaultStyles) }, "HSV"),
        React.createElement("div", { id: "rbgcp-color-model-cmyk-btn".concat(pickerIdSuffix), onClick: function (e) { return handleInputType(e, 'cmyk'); }, style: modalBtnStyles(inputType === 'cmyk', defaultStyles) }, "CMYK")));
};
var Controls = function (_a) {
    var _b, _c;
    var locales = _a.locales, _d = _a.hideEyeDrop, hideEyeDrop = _d === void 0 ? false : _d, _e = _a.hideAdvancedSliders, hideAdvancedSliders = _e === void 0 ? false : _e, _f = _a.hideColorGuide, hideColorGuide = _f === void 0 ? false : _f, _g = _a.hideInputType, hideInputType = _g === void 0 ? false : _g, _h = _a.hideColorTypeBtns, hideColorTypeBtns = _h === void 0 ? false : _h, _j = _a.hideGradientControls, hideGradientControls = _j === void 0 ? false : _j, _k = _a.hideGradientType, hideGradientType = _k === void 0 ? false : _k, _l = _a.hideGradientAngle, hideGradientAngle = _l === void 0 ? false : _l, _m = _a.hideGradientStop, hideGradientStop = _m === void 0 ? false : _m;
    var _o = usePicker(), config = _o.config, onChange = _o.onChange, isGradient = _o.isGradient, handleChange = _o.handleChange, previous = _o.previous, defaultStyles = _o.defaultStyles, pickerIdSuffix = _o.pickerIdSuffix;
    var defaultColor = config.defaultColor, defaultGradient = config.defaultGradient;
    var _p = useState(false), openComparibles = _p[0], setOpenComparibles = _p[1];
    var _q = useState(false), openInputType = _q[0], setOpenInputType = _q[1];
    var _r = useState(false), openAdvanced = _r[0], setOpenAdvanced = _r[1];
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
            return (React.createElement(GradientControls, { hideGradientType: hideGradientType, hideGradientAngle: hideGradientAngle, hideGradientStop: hideGradientStop }));
        }
        else {
            return null;
        }
    }
    else {
        return (React.createElement("div", { style: { paddingBottom: 4 } },
            React.createElement("div", { style: {
                    width: '100%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                }, id: "rbgcp-controls-wrapper".concat(pickerIdSuffix) },
                React.createElement(ColorTypeBtns, { hideColorTypeBtns: hideColorTypeBtns, setGradient: setGradient, isGradient: isGradient, setSolid: setSolid, locales: locales }),
                !allRightControlsHidden && (React.createElement("div", { style: __assign({ display: noTools ? 'none' : '' }, defaultStyles.rbgcpControlBtnWrapper), id: "rbgcp-control-rightside-wrapper".concat(pickerIdSuffix) },
                    !hideEyeDrop && React.createElement(EyeDropper, { onSelect: handleChange }),
                    !hideAdvancedSliders && (React.createElement("div", { id: "rbgcp-advanced-btn".concat(pickerIdSuffix), onClick: function () { return setOpenAdvanced(!openAdvanced); }, 
                        // className="rbgcp-control-btn rbgcp-advanced-btn"
                        style: controlBtnStyles(openAdvanced, defaultStyles) },
                        React.createElement(SlidersIcon, { color: openAdvanced ? '#568CF5' : '' }))),
                    !hideColorGuide && (React.createElement("div", { style: controlBtnStyles(openComparibles, defaultStyles), onClick: function () { return setOpenComparibles(!openComparibles); }, 
                        // className="rbgcp-control-btn rbgcp-comparibles-btn"
                        id: "rbgcp-comparibles-btn".concat(pickerIdSuffix) },
                        React.createElement(PaletteIcon, { color: openComparibles ? '#568CF5' : '' }))),
                    !hideInputType && (React.createElement("div", { id: "rbgcp-color-model-btn".concat(pickerIdSuffix), onClick: function () { return setOpenInputType(!openInputType); }, 
                        // className="rbgcp-control-btn rbgcp-color-model-btn"
                        style: controlBtnStyles(openInputType, defaultStyles) },
                        React.createElement(InputsIcon, { color: openInputType ? '#568CF5' : '' }),
                        React.createElement(InputTypeDropdown, { openInputType: openInputType, setOpenInputType: setOpenInputType })))))),
            !hideAdvancedSliders && (React.createElement(AdvancedControls, { openAdvanced: openAdvanced })),
            !hideColorGuide && (React.createElement(ComparibleColors, { openComparibles: openComparibles })),
            isGradient && !hideGradientControls && (React.createElement(GradientControls, { hideGradientType: hideGradientType, hideGradientAngle: hideGradientAngle, hideGradientStop: hideGradientStop }))));
    }
};
export default Controls;
