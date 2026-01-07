import { gradientParser } from './gradientParser.js';
export var low = function (color) {
    return color.value.toLowerCase();
};
export var high = function (color) {
    return color.value.toUpperCase();
};
export var getColors = function (value, defaultColor, defaultGradient) {
    var isGradient = value === null || value === void 0 ? void 0 : value.includes('gradient');
    if (isGradient) {
        var isConic = value === null || value === void 0 ? void 0 : value.includes('conic');
        var safeValue = !isConic ? value : defaultGradient;
        if (isConic) {
            console.log('Sorry we cant handle conic gradients yet');
        }
        var obj = gradientParser(safeValue);
        return obj === null || obj === void 0 ? void 0 : obj.colorStops;
    }
    else {
        var safeValue = value || defaultColor;
        return [{ value: safeValue }];
    }
};
export var formatInputValues = function (value, min, max) {
    return isNaN(value) ? min : value < min ? min : value > max ? max : value;
};
export var round = function (val) {
    return Math.round(val);
};
