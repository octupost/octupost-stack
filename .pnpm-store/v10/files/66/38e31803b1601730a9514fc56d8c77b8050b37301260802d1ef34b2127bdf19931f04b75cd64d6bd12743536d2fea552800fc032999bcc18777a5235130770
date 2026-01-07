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
import tc from 'tinycolor2';
import { useState, useEffect } from 'react';
import { rgb2cmyk } from '../utils/converters.js';
import { isUpperCase, getDetails, getColorObj } from '../utils/utils.js';
import { low, high, getColors, formatInputValues } from '../utils/formatters.js';
export var useColorPicker = function (value, onChange, config) {
    var _a = config !== null && config !== void 0 ? config : {}, _b = _a.defaultColor, defaultColor = _b === void 0 ? 'rgba(175, 51, 242, 1)' : _b, _c = _a.defaultGradient, defaultGradient = _c === void 0 ? 'linear-gradient(90deg, rgba(2,0,36,1) 0%, rgba(9,9,121,1) 35%, rgba(0,212,255,1) 100%)' : _c;
    var colors = getColors(value, defaultColor, defaultGradient);
    var _d = getDetails(value), degrees = _d.degrees, degreeStr = _d.degreeStr, isGradient = _d.isGradient, gradientType = _d.gradientType;
    var _e = getColorObj(colors, defaultGradient), currentColor = _e.currentColor, selectedColor = _e.selectedColor, currentLeft = _e.currentLeft;
    var _f = useState([]), previousColors = _f[0], setPreviousColors = _f[1];
    var getGradientObject = function (currentValue) {
        if (currentValue) {
            colors = getColors(currentValue, defaultColor, defaultGradient);
        }
        if (value) {
            if (isGradient) {
                return {
                    isGradient: true,
                    gradientType: gradientType,
                    degrees: degreeStr,
                    colors: colors === null || colors === void 0 ? void 0 : colors.map(function (c) {
                        var _a;
                        return (__assign(__assign({}, c), { value: (_a = c.value) === null || _a === void 0 ? void 0 : _a.toLowerCase() }));
                    }),
                };
            }
            else {
                return {
                    isGradient: false,
                    gradientType: null,
                    degrees: null,
                    colors: colors === null || colors === void 0 ? void 0 : colors.map(function (c) {
                        var _a;
                        return (__assign(__assign({}, c), { value: (_a = c.value) === null || _a === void 0 ? void 0 : _a.toLowerCase() }));
                    }),
                };
            }
        }
        else {
            console.log('RBGCP ERROR - YOU MUST PASS A VALUE AND CALLBACK TO THE useColorPicker HOOK');
        }
    };
    var tiny = tc(currentColor);
    var _g = tiny.toRgb(), r = _g.r, g = _g.g, b = _g.b, a = _g.a;
    var _h = tiny.toHsl(), h = _h.h, s = _h.s, l = _h.l;
    useEffect(function () {
        var _a;
        if (((_a = tc(currentColor)) === null || _a === void 0 ? void 0 : _a.isValid()) && previousColors[0] !== currentColor) {
            // @ts-expect-error - currentColor type issue
            setPreviousColors(__spreadArray([currentColor], previousColors.slice(0, 19), true));
        }
    }, [currentColor, previousColors]);
    var setLinear = function () {
        var remaining = value.split(/,(.+)/)[1];
        onChange("linear-gradient(90deg, ".concat(remaining));
    };
    var setRadial = function () {
        var remaining = value.split(/,(.+)/)[1];
        onChange("radial-gradient(circle, ".concat(remaining));
    };
    var setDegrees = function (newDegrees) {
        var remaining = value.split(/,(.+)/)[1];
        onChange("linear-gradient(".concat(formatInputValues(newDegrees, 0, 360), "deg, ").concat(remaining));
        if (gradientType !== 'linear-gradient') {
            console.log('Warning: you are updating degrees when the gradient type is not linear. This will change the gradients type which may be undesired');
        }
    };
    var setSolid = function (startingColor) {
        var _a;
        var newValue = (_a = startingColor !== null && startingColor !== void 0 ? startingColor : defaultColor) !== null && _a !== void 0 ? _a : 'rgba(175, 51, 242, 1)';
        onChange(newValue);
    };
    var setGradient = function (startingGradiant) {
        var _a;
        var newValue = (_a = startingGradiant !== null && startingGradiant !== void 0 ? startingGradiant : defaultGradient) !== null && _a !== void 0 ? _a : 'linear-gradient(90deg, rgba(2,0,36,1) 0%, rgba(9,9,121,1) 35%, rgba(0,212,255,1) 100%)';
        onChange(newValue);
    };
    var createGradientStr = function (newColors) {
        var sorted = newColors.sort(function (a, b) { return a.left - b.left; });
        var colorString = sorted === null || sorted === void 0 ? void 0 : sorted.map(function (cc) { return "".concat(cc === null || cc === void 0 ? void 0 : cc.value, " ").concat(cc.left, "%"); });
        onChange("".concat(gradientType, "(").concat(degreeStr, ", ").concat(colorString.join(', '), ")"));
    };
    var handleGradient = function (newColor, left) {
        var remaining = colors === null || colors === void 0 ? void 0 : colors.filter(function (c) { return !isUpperCase(c.value); });
        var newColors = __spreadArray([
            { value: newColor.toUpperCase(), left: left !== null && left !== void 0 ? left : currentLeft }
        ], remaining, true);
        createGradientStr(newColors);
    };
    var handleChange = function (newColor) {
        newColor = newColor === null || newColor === void 0 ? void 0 : newColor.replace(/\s+/g, '');
        if (isGradient) {
            handleGradient(newColor);
        }
        else {
            onChange(newColor);
        }
    };
    var setR = function (newR) {
        var newVal = formatInputValues(newR, 0, 255);
        handleChange("rgba(".concat(newVal, ", ").concat(g, ", ").concat(b, ", ").concat(a, ")"));
    };
    var setG = function (newG) {
        var newVal = formatInputValues(newG, 0, 255);
        handleChange("rgba(".concat(r, ", ").concat(newVal, ", ").concat(b, ", ").concat(a, ")"));
    };
    var setB = function (newB) {
        var newVal = formatInputValues(newB, 0, 255);
        handleChange("rgba(".concat(r, ", ").concat(g, ", ").concat(newVal, ", ").concat(a, ")"));
    };
    var setA = function (newA) {
        var newVal = formatInputValues(newA, 0, 100);
        handleChange("rgba(".concat(r, ", ").concat(g, ", ").concat(b, ", ").concat(newVal / 100, ")"));
    };
    var setHue = function (newHue) {
        var newVal = formatInputValues(newHue, 0, 360);
        var tinyNew = tc({ h: newVal, s: s, l: l });
        var _a = tinyNew.toRgb(), r = _a.r, g = _a.g, b = _a.b;
        handleChange("rgba(".concat(r, ", ").concat(g, ", ").concat(b, ", ").concat(a, ")"));
    };
    var setSaturation = function (newSat) {
        var newVal = formatInputValues(newSat, 0, 100);
        var tinyNew = tc({ h: h, s: newVal / 100, l: l });
        var _a = tinyNew.toRgb(), r = _a.r, g = _a.g, b = _a.b;
        handleChange("rgba(".concat(r, ", ").concat(g, ", ").concat(b, ", ").concat(a, ")"));
    };
    var setLightness = function (newLight) {
        var newVal = formatInputValues(newLight, 0, 100);
        var tinyNew = tc({ h: h, s: s, l: newVal / 100 });
        if (tinyNew === null || tinyNew === void 0 ? void 0 : tinyNew.isValid()) {
            var _a = tinyNew.toRgb(), r_1 = _a.r, g_1 = _a.g, b_1 = _a.b;
            handleChange("rgba(".concat(r_1, ", ").concat(g_1, ", ").concat(b_1, ", ").concat(a, ")"));
        }
        else {
            console.log('The new color was invalid, perhaps the lightness you passed in was a decimal? Please pass the new value between 0 - 100');
        }
    };
    var valueToHSL = function () {
        return tiny.toHslString();
    };
    var valueToHSV = function () {
        return tiny.toHsvString();
    };
    var valueToHex = function () {
        return tiny.toHexString();
    };
    var valueToCmyk = function () {
        var _a = rgb2cmyk(r, g, b), c = _a.c, m = _a.m, y = _a.y, k = _a.k;
        return "cmyk(".concat(c, ", ").concat(m, ", ").concat(y, ", ").concat(k, ")");
    };
    var setSelectedPoint = function (index) {
        if (isGradient) {
            var newGradStr = colors === null || colors === void 0 ? void 0 : colors.map(function (cc, i) { return (__assign(__assign({}, cc), { value: i === index ? high(cc) : low(cc) })); });
            createGradientStr(newGradStr);
        }
        else {
            console.log('This function is only relevant when the picker is in gradient mode');
        }
    };
    var addPoint = function (left) {
        var newColors = __spreadArray(__spreadArray([], colors.map(function (c) { return (__assign(__assign({}, c), { value: low(c) })); }), true), [
            { value: currentColor, left: left },
        ], false);
        createGradientStr(newColors);
        if (!left) {
            console.log('You did not pass a stop value (left amount) for the new color point so it defaulted to 50');
        }
    };
    var deletePoint = function (index) {
        if ((colors === null || colors === void 0 ? void 0 : colors.length) > 2) {
            var pointToDelete_1 = index !== null && index !== void 0 ? index : selectedColor;
            var remaining = colors === null || colors === void 0 ? void 0 : colors.filter(function (rc, i) { return i !== pointToDelete_1; });
            createGradientStr(remaining);
            if (!index) {
                console.log('You did not pass in the index of the point you wanted to delete so the function default to the currently selected point');
            }
        }
        else {
            console.log('A gradient must have atleast two colors, disable your delete button when necessary');
        }
    };
    var setPointLeft = function (left) {
        handleGradient(currentColor, formatInputValues(left, 0, 100));
    };
    var rgbaArr = [r, g, b, a];
    var hslArr = [h, s, l];
    return {
        setR: setR,
        setG: setG,
        setB: setB,
        setA: setA,
        setHue: setHue,
        addPoint: addPoint,
        setSolid: setSolid,
        setLinear: setLinear,
        setRadial: setRadial,
        valueToHSL: valueToHSL,
        valueToHSV: valueToHSV,
        valueToHex: valueToHex,
        valueToCmyk: valueToCmyk,
        setDegrees: setDegrees,
        setGradient: setGradient,
        setLightness: setLightness,
        setSaturation: setSaturation,
        setSelectedPoint: setSelectedPoint,
        deletePoint: deletePoint,
        isGradient: isGradient,
        gradientType: gradientType,
        degrees: degrees,
        setPointLeft: setPointLeft,
        currentLeft: currentLeft,
        rgbaArr: rgbaArr,
        hslArr: hslArr,
        handleChange: handleChange,
        previousColors: previousColors,
        getGradientObject: getGradientObject,
        selectedPoint: selectedColor,
    };
};
