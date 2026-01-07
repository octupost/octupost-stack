'use client';
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
import React from 'react';
import PickerContextWrapper from '../context.js';
import Picker from './Picker.js';
import { defaultLocales } from '../constants.js';
import { objectToString } from '../utils/utils.js';
import { getStyles } from '../styles/styles.js';
export function ColorPicker(_a) {
    var idSuffix = _a.idSuffix, _b = _a.value, value = _b === void 0 ? 'rgba(175, 51, 242, 1)' : _b, onChange = _a.onChange, _c = _a.hideControls, hideControls = _c === void 0 ? false : _c, _d = _a.hideInputs, hideInputs = _d === void 0 ? false : _d, _e = _a.hideOpacity, hideOpacity = _e === void 0 ? false : _e, _f = _a.hidePresets, hidePresets = _f === void 0 ? false : _f, _g = _a.hideHue, hideHue = _g === void 0 ? false : _g, _h = _a.presets, presets = _h === void 0 ? [] : _h, _j = _a.hideEyeDrop, hideEyeDrop = _j === void 0 ? false : _j, _k = _a.hideAdvancedSliders, hideAdvancedSliders = _k === void 0 ? false : _k, _l = _a.hideColorGuide, hideColorGuide = _l === void 0 ? false : _l, _m = _a.hideInputType, hideInputType = _m === void 0 ? false : _m, _o = _a.hideColorTypeBtns, hideColorTypeBtns = _o === void 0 ? false : _o, _p = _a.hideGradientType, hideGradientType = _p === void 0 ? false : _p, _q = _a.hideGradientAngle, hideGradientAngle = _q === void 0 ? false : _q, _r = _a.hideGradientStop, hideGradientStop = _r === void 0 ? false : _r, _s = _a.hideGradientControls, hideGradientControls = _s === void 0 ? false : _s, _t = _a.locales, locales = _t === void 0 ? defaultLocales : _t, _u = _a.width, width = _u === void 0 ? 294 : _u, _v = _a.height, height = _v === void 0 ? 294 : _v, _w = _a.style, style = _w === void 0 ? {} : _w, className = _a.className, _x = _a.disableDarkMode, disableDarkMode = _x === void 0 ? false : _x, _y = _a.disableLightMode, disableLightMode = _y === void 0 ? false : _y, _z = _a.hidePickerSquare, hidePickerSquare = _z === void 0 ? false : _z, _0 = _a.showHexAlpha, showHexAlpha = _0 === void 0 ? false : _0, _1 = _a.config, config = _1 === void 0 ? {} : _1;
    var safeValue = objectToString(value);
    var isDarkMode = typeof window === 'undefined' || disableDarkMode
        ? false
        : window.matchMedia('(prefers-color-scheme: dark)').matches ||
            disableLightMode
            ? true
            : false;
    // const contRef = useRef<HTMLDivElement>(null)
    var defaultStyles = getStyles(isDarkMode, style);
    var pickerIdSuffix = isDarkMode
        ? "-dark".concat(idSuffix ? "-".concat(idSuffix) : '')
        : idSuffix
            ? "-".concat(idSuffix)
            : '';
    return (React.createElement("div", { 
        // ref={contRef}
        className: className, style: __assign(__assign({}, defaultStyles.body), { width: width }) },
        React.createElement(PickerContextWrapper, { value: safeValue, onChange: onChange, squareWidth: width, passedConfig: config, squareHeight: height, isDarkMode: isDarkMode, hideOpacity: hideOpacity, showHexAlpha: showHexAlpha, defaultStyles: defaultStyles, pickerIdSuffix: pickerIdSuffix },
            React.createElement(Picker, { hideControls: hideControls, hideInputs: hideInputs, hidePresets: hidePresets, hideOpacity: hideOpacity, hideHue: hideHue, presets: presets, hideEyeDrop: hideEyeDrop, hideAdvancedSliders: hideAdvancedSliders, hideColorGuide: hideColorGuide, hideInputType: hideInputType, hideColorTypeBtns: hideColorTypeBtns, hideGradientType: hideGradientType, hideGradientAngle: hideGradientAngle, hideGradientStop: hideGradientStop, hideGradientControls: hideGradientControls, hidePickerSquare: hidePickerSquare, locales: locales }))));
}
