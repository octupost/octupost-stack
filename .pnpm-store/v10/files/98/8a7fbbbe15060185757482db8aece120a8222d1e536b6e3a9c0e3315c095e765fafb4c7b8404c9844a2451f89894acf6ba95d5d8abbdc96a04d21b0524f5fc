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
Object.defineProperty(exports, "__esModule", { value: true });
exports.getDetails = exports.getColorObj = exports.objectToString = exports.isUpperCase = exports.safeBounds = void 0;
exports.getHandleValue = getHandleValue;
exports.computeSquareXY = computeSquareXY;
exports.computePickerPosition = computePickerPosition;
var formatters_js_1 = require("./formatters.js");
var safeBounds = function (e) {
    var client = e.target.parentNode.getBoundingClientRect();
    var className = e.target.className;
    var adjuster = className === 'c-resize ps-rl' ? 15 : 0;
    return {
        offsetLeft: (client === null || client === void 0 ? void 0 : client.x) + adjuster,
        offsetTop: client === null || client === void 0 ? void 0 : client.y,
        clientWidth: client === null || client === void 0 ? void 0 : client.width,
        clientHeight: client === null || client === void 0 ? void 0 : client.height,
    };
};
exports.safeBounds = safeBounds;
function getHandleValue(e, barSize) {
    var _a = (0, exports.safeBounds)(e), offsetLeft = _a.offsetLeft, clientWidth = _a.clientWidth;
    var pos = e.clientX - offsetLeft - barSize / 2;
    var adjuster = clientWidth - 18;
    var bounded = (0, formatters_js_1.formatInputValues)(pos, 0, adjuster);
    return Math.round(bounded / (adjuster / 100));
}
function computeSquareXY(s, v, squareWidth, squareHeight, crossSize) {
    var x = s * squareWidth - crossSize / 2;
    var y = ((100 - v) / 100) * squareHeight - crossSize / 2;
    return [x, y];
}
var getClientXY = function (e) {
    if (e.clientX) {
        return { clientX: e.clientX, clientY: e.clientY };
    }
    else {
        var touch = e.touches[0] || {};
        return { clientX: touch.clientX, clientY: touch.clientY };
    }
};
function computePickerPosition(e, crossSize) {
    var _a = (0, exports.safeBounds)(e), offsetLeft = _a.offsetLeft, offsetTop = _a.offsetTop, clientWidth = _a.clientWidth, clientHeight = _a.clientHeight;
    var _b = getClientXY(e), clientX = _b.clientX, clientY = _b.clientY;
    var getX = function () {
        var xPos = clientX - offsetLeft - crossSize / 2;
        return (0, formatters_js_1.formatInputValues)(xPos, -9, clientWidth - 10);
    };
    var getY = function () {
        var yPos = clientY - offsetTop - crossSize / 2;
        return (0, formatters_js_1.formatInputValues)(yPos, -9, clientHeight - 10);
    };
    return [getX(), getY()];
}
// export const getGradientType = (value: string) => {
//   return value?.split('(')[0]
// }
var isUpperCase = function (str) {
    var _a;
    return (str === null || str === void 0 ? void 0 : str[0]) === ((_a = str === null || str === void 0 ? void 0 : str[0]) === null || _a === void 0 ? void 0 : _a.toUpperCase());
};
exports.isUpperCase = isUpperCase;
// export const compareGradients = (g1: string, g2: string) => {
//   const ng1 = g1?.toLowerCase()?.replaceAll(' ', '')
//   const ng2 = g2?.toLowerCase()?.replaceAll(' ', '')
//   if (ng1 === ng2) {
//     return true
//   } else {
//     return false
//   }
// }
var convertShortHandDeg = function (dir) {
    if (dir === 'to top') {
        return 0;
    }
    else if (dir === 'to bottom') {
        return 180;
    }
    else if (dir === 'to left') {
        return 270;
    }
    else if (dir === 'to right') {
        return 90;
    }
    else if (dir === 'to top right') {
        return 45;
    }
    else if (dir === 'to bottom right') {
        return 135;
    }
    else if (dir === 'to bottom left') {
        return 225;
    }
    else if (dir === 'to top left') {
        return 315;
    }
    else {
        var safeDir = dir || 0;
        return parseInt(safeDir);
    }
};
var objectToString = function (value) {
    var _a, _b, _c, _d, _e;
    if (typeof value === 'string') {
        return value;
    }
    else {
        if ((_a = value === null || value === void 0 ? void 0 : value.type) === null || _a === void 0 ? void 0 : _a.includes('gradient')) {
            var sorted = (_b = value === null || value === void 0 ? void 0 : value.colorStops) === null || _b === void 0 ? void 0 : _b.sort(function (a, b) { return (a === null || a === void 0 ? void 0 : a.left) - (b === null || b === void 0 ? void 0 : b.left); });
            var string = (_c = sorted === null || sorted === void 0 ? void 0 : sorted.map(function (c) { return "".concat(c === null || c === void 0 ? void 0 : c.value, " ").concat(c === null || c === void 0 ? void 0 : c.left, "%"); })) === null || _c === void 0 ? void 0 : _c.join(', ');
            var type = value === null || value === void 0 ? void 0 : value.type;
            var degs = convertShortHandDeg((_d = value === null || value === void 0 ? void 0 : value.orientation) === null || _d === void 0 ? void 0 : _d.value);
            var gradientStr = type === 'linear-gradient' ? "".concat(degs, "deg") : 'circle';
            return "".concat(type, "(").concat(gradientStr, ", ").concat(string, ")");
        }
        else {
            var color = ((_e = value === null || value === void 0 ? void 0 : value.colorStops[0]) === null || _e === void 0 ? void 0 : _e.value) || 'rgba(175, 51, 242, 1)';
            return color;
        }
    }
};
exports.objectToString = objectToString;
var getColorObj = function (colors, defaultGradient) {
    var idxCols = colors === null || colors === void 0 ? void 0 : colors.map(function (c, i) { return (__assign(__assign({}, c), { index: i })); });
    var upperObj = idxCols === null || idxCols === void 0 ? void 0 : idxCols.find(function (c) { return (0, exports.isUpperCase)(c.value); });
    var ccObj = upperObj || idxCols[0];
    return {
        currentColor: (ccObj === null || ccObj === void 0 ? void 0 : ccObj.value) || defaultGradient,
        selectedColor: (ccObj === null || ccObj === void 0 ? void 0 : ccObj.index) || 0,
        currentLeft: (ccObj === null || ccObj === void 0 ? void 0 : ccObj.left) || 0,
    };
};
exports.getColorObj = getColorObj;
var getDegrees = function (value) {
    var _a;
    var s1 = value === null || value === void 0 ? void 0 : value.split(',')[0];
    var s2 = (_a = s1 === null || s1 === void 0 ? void 0 : s1.split('(')[1]) === null || _a === void 0 ? void 0 : _a.replace('deg', '');
    return convertShortHandDeg(s2);
};
var getDetails = function (value) {
    var isGradient = value === null || value === void 0 ? void 0 : value.includes('gradient');
    var gradientType = value === null || value === void 0 ? void 0 : value.split('(')[0];
    var degrees = getDegrees(value);
    var degreeStr = gradientType === 'linear-gradient' ? "".concat(degrees, "deg") : 'circle';
    return {
        degrees: degrees,
        degreeStr: degreeStr,
        isGradient: isGradient,
        gradientType: gradientType,
    };
};
exports.getDetails = getDetails;
