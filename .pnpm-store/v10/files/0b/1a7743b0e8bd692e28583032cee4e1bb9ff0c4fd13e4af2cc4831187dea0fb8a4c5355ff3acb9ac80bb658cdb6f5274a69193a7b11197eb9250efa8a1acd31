"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.round = exports.formatInputValues = exports.getColors = exports.high = exports.low = void 0;
var gradientParser_js_1 = require("./gradientParser.js");
var low = function (color) {
    return color.value.toLowerCase();
};
exports.low = low;
var high = function (color) {
    return color.value.toUpperCase();
};
exports.high = high;
var getColors = function (value, defaultColor, defaultGradient) {
    var isGradient = value === null || value === void 0 ? void 0 : value.includes('gradient');
    if (isGradient) {
        var isConic = value === null || value === void 0 ? void 0 : value.includes('conic');
        var safeValue = !isConic ? value : defaultGradient;
        if (isConic) {
            console.log('Sorry we cant handle conic gradients yet');
        }
        var obj = (0, gradientParser_js_1.gradientParser)(safeValue);
        return obj === null || obj === void 0 ? void 0 : obj.colorStops;
    }
    else {
        var safeValue = value || defaultColor;
        return [{ value: safeValue }];
    }
};
exports.getColors = getColors;
var formatInputValues = function (value, min, max) {
    return isNaN(value) ? min : value < min ? min : value > max ? max : value;
};
exports.formatInputValues = formatInputValues;
var round = function (val) {
    return Math.round(val);
};
exports.round = round;
