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
var __spreadArray = (this && this.__spreadArray) || function (to, from, pack) {
    if (pack || arguments.length === 2) for (var i = 0, l = from.length, ar; i < l; i++) {
        if (ar || !(i in from)) {
            if (!ar) ar = Array.prototype.slice.call(from, 0, i);
            ar[i] = from[i];
        }
    }
    return to.concat(ar || Array.prototype.slice.call(from));
};
import React, { createContext, useContext, useEffect, useState, } from 'react';
import { isUpperCase, getColorObj, getDetails } from './utils/utils.js';
import { low, high, getColors } from './utils/formatters.js';
import tinycolor from 'tinycolor2';
var PickerContext = createContext(null);
export default function PickerContextWrapper(_a) {
    var _b, _c, _d, _e;
    var value = _a.value, children = _a.children, onChange = _a.onChange, isDarkMode = _a.isDarkMode, squareWidth = _a.squareWidth, hideOpacity = _a.hideOpacity, showHexAlpha = _a.showHexAlpha, squareHeight = _a.squareHeight, passedConfig = _a.passedConfig, defaultStyles = _a.defaultStyles, pickerIdSuffix = _a.pickerIdSuffix;
    var config = {
        barSize: (_b = passedConfig.barSize) !== null && _b !== void 0 ? _b : defaultConfig.barSize,
        crossSize: (_c = passedConfig.crossSize) !== null && _c !== void 0 ? _c : defaultConfig.crossSize,
        defaultColor: (_d = passedConfig.defaultColor) !== null && _d !== void 0 ? _d : defaultConfig.defaultColor,
        defaultGradient: (_e = passedConfig.defaultGradient) !== null && _e !== void 0 ? _e : defaultConfig.defaultGradient,
    };
    var colors = getColors(value, config.defaultColor, config.defaultGradient);
    var _f = getDetails(value), degrees = _f.degrees, degreeStr = _f.degreeStr, isGradient = _f.isGradient, gradientType = _f.gradientType;
    var _g = getColorObj(colors, config.defaultGradient), currentColor = _g.currentColor, selectedColor = _g.selectedColor, currentLeft = _g.currentLeft;
    var _h = useState('rgb'), inputType = _h[0], setInputType = _h[1];
    var _j = useState({}), previous = _j[0], setPrevious = _j[1];
    var tinyColor = tinycolor(currentColor);
    var rgba = tinyColor.toRgb();
    var hsv = tinyColor.toHsv();
    var _k = useState(__assign(__assign({}, rgba), hsv)), hc = _k[0], setHc = _k[1];
    useEffect(function () {
        if ((hsv === null || hsv === void 0 ? void 0 : hsv.s) === 0) {
            setHc(__assign(__assign(__assign({}, rgba), hsv), { h: hc === null || hc === void 0 ? void 0 : hc.h }));
        }
        else {
            setHc(__assign(__assign({}, rgba), hsv));
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [currentColor]);
    var createGradientStr = function (newColors) {
        var sorted = newColors.sort(function (a, b) { return a.left - b.left; });
        var colorString = sorted === null || sorted === void 0 ? void 0 : sorted.map(function (cc) { return "".concat(cc === null || cc === void 0 ? void 0 : cc.value, " ").concat(cc.left, "%"); });
        var newGrade = "".concat(gradientType, "(").concat(degreeStr, ", ").concat(colorString.join(', '), ")");
        setPrevious(__assign(__assign({}, previous), { gradient: newGrade }));
        onChange(newGrade);
    };
    var handleGradient = function (newColor, left) {
        var remaining = colors === null || colors === void 0 ? void 0 : colors.filter(function (c) { return !isUpperCase(c.value); });
        var newColors = __spreadArray([
            { value: newColor.toUpperCase(), left: left !== null && left !== void 0 ? left : currentLeft }
        ], remaining, true);
        createGradientStr(newColors);
    };
    var handleChange = function (newColor) {
        if (isGradient) {
            handleGradient(newColor);
        }
        else {
            setPrevious(__assign(__assign({}, previous), { color: newColor }));
            onChange(newColor);
        }
    };
    var deletePoint = function () {
        if ((colors === null || colors === void 0 ? void 0 : colors.length) > 2) {
            var formatted = colors === null || colors === void 0 ? void 0 : colors.map(function (fc, i) { return (__assign(__assign({}, fc), { value: i === selectedColor - 1 ? high(fc) : low(fc) })); });
            var remaining = formatted === null || formatted === void 0 ? void 0 : formatted.filter(function (_, i) { return i !== selectedColor; });
            createGradientStr(remaining);
        }
    };
    var pickerContext = {
        hc: hc,
        setHc: setHc,
        value: value,
        colors: colors,
        config: config,
        degrees: degrees,
        onChange: onChange,
        previous: previous,
        inputType: inputType,
        tinyColor: tinyColor,
        isDarkMode: isDarkMode,
        isGradient: isGradient,
        squareWidth: squareWidth,
        hideOpacity: hideOpacity,
        currentLeft: currentLeft,
        deletePoint: deletePoint,
        showHexAlpha: showHexAlpha,
        squareHeight: squareHeight,
        setInputType: setInputType,
        gradientType: gradientType,
        handleChange: handleChange,
        currentColor: currentColor,
        selectedColor: selectedColor,
        defaultStyles: defaultStyles,
        handleGradient: handleGradient,
        pickerIdSuffix: pickerIdSuffix,
        createGradientStr: createGradientStr,
    };
    return (React.createElement(PickerContext.Provider, { value: pickerContext }, children));
}
export function usePicker() {
    var pickerContext = useContext(PickerContext);
    if (!pickerContext) {
        throw new Error('usePicker has to be used within <PickerContext.Provider>');
    }
    return pickerContext;
}
var defaultConfig = {
    barSize: 18,
    crossSize: 18,
    inputSize: 40,
    delay: 150,
    defaultColor: 'rgba(175, 51, 242, 1)',
    defaultGradient: 'linear-gradient(90deg, rgba(2,0,36,1) 0%, rgba(9,9,121,1) 35%, rgba(0,212,255,1) 100%)',
};
