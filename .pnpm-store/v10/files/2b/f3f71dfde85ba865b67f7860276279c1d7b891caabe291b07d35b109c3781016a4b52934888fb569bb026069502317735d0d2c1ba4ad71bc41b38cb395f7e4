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
var __spreadArray = (this && this.__spreadArray) || function (to, from, pack) {
    if (pack || arguments.length === 2) for (var i = 0, l = from.length, ar; i < l; i++) {
        if (ar || !(i in from)) {
            if (!ar) ar = Array.prototype.slice.call(from, 0, i);
            ar[i] = from[i];
        }
    }
    return to.concat(ar || Array.prototype.slice.call(from));
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.gradientParser = void 0;
var formatters_js_1 = require("./formatters.js");
var utils_js_1 = require("./utils.js");
var tinycolor2_1 = __importDefault(require("tinycolor2"));
var gradientParser = function (input) {
    if (input === void 0) { input = ''; }
    var tokens = {
        linearGradient: /^(-(webkit|o|ms|moz)-)?(linear-gradient)/i,
        repeatingLinearGradient: /^(-(webkit|o|ms|moz)-)?(repeating-linear-gradient)/i,
        radialGradient: /^(-(webkit|o|ms|moz)-)?(radial-gradient)/i,
        repeatingRadialGradient: /^(-(webkit|o|ms|moz)-)?(repeating-radial-gradient)/i,
        sideOrCorner: /^to (left (top|bottom)|right (top|bottom)|top (left|right)|bottom (left|right)|left|right|top|bottom)/i,
        extentKeywords: /^(closest-side|closest-corner|farthest-side|farthest-corner|contain|cover)/,
        positionKeywords: /^(left|center|right|top|bottom)/i,
        pixelValue: /^(-?(([0-9]*\.[0-9]+)|([0-9]+\.?)))px/,
        percentageValue: /^(-?(([0-9]*\.[0-9]+)|([0-9]+\.?)))%/,
        emValue: /^(-?(([0-9]*\.[0-9]+)|([0-9]+\.?)))em/,
        angleValue: /^(-?(([0-9]*\.[0-9]+)|([0-9]+\.?)))deg/,
        startCall: /^\(/,
        endCall: /^\)/,
        comma: /^,/,
        hexColor: /^#([0-9a-fA-F]+)/,
        literalColor: /^([a-zA-Z]+)/,
        rgbColor: /^rgb/i,
        spacedRgbColor: /^(\d{1,3})\s+(\d{1,3})\s+(\d{1,3})\s+\/\s+([0-1](\.\d+)?)/,
        rgbaColor: /^rgba/i,
        hslColor: /^hsl/i,
        hsvColor: /^hsv/i,
        number: /^(([0-9]*\.[0-9]+)|([0-9]+\.?))/,
    };
    function error(msg) {
        var err = new Error(input + ': ' + msg);
        // err.source = input
        throw err;
    }
    function consume(size) {
        input = input.substr(size);
    }
    function scan(regexp) {
        var blankCaptures = /^[\n\r\t\s]+/.exec(input);
        if (blankCaptures) {
            consume(blankCaptures[0].length);
        }
        var captures = regexp.exec(input);
        if (captures) {
            consume(captures[0].length);
        }
        return captures;
    }
    function matchListing(matcher) {
        var captures = matcher();
        var result = [];
        if (captures) {
            result.push(captures);
            while (scan(tokens.comma)) {
                captures = matcher();
                if (captures) {
                    result.push(captures);
                }
                else {
                    error('One extra comma');
                }
            }
        }
        return result;
    }
    function match(type, pattern, captureIndex) {
        var captures = scan(pattern);
        if (captures) {
            return {
                type: type,
                value: captures[captureIndex],
            };
        }
    }
    function matchHexColor() {
        var hexObj = match('hex', tokens.hexColor, 1);
        if (hexObj === null || hexObj === void 0 ? void 0 : hexObj.value) {
            var _a = (0, tinycolor2_1.default)(hexObj === null || hexObj === void 0 ? void 0 : hexObj.value).toRgb(), r = _a.r, g = _a.g, b = _a.b, a = _a.a;
            return {
                value: "rgba(".concat(r, ", ").concat(g, ", ").concat(b, ", ").concat(a, ")"),
            };
        }
    }
    var checkCaps = function (val) {
        var capIt = (0, utils_js_1.isUpperCase)(val === null || val === void 0 ? void 0 : val[0]);
        return {
            value: "".concat(capIt ? 'RGBA' : 'rgba', "(").concat(matchListing(matchNumber), ")"),
        };
    };
    function matchCall(pattern, callback) {
        var captures = scan(pattern);
        if (captures) {
            if (!scan(tokens.startCall)) {
                error('Missing (');
            }
            var result = callback(captures);
            if (!scan(tokens.endCall)) {
                error('Missing )');
            }
            return result;
        }
    }
    function matchHSLColor() {
        return matchCall(tokens.hslColor, convertHsl);
    }
    function matchRGBAColor() {
        return matchCall(tokens.rgbaColor, checkCaps);
    }
    function matchRGBColor() {
        return matchCall(tokens.rgbColor, convertRgb);
    }
    function matchLiteralColor() {
        var litObj = match('literal', tokens.literalColor, 0);
        if (litObj === null || litObj === void 0 ? void 0 : litObj.value) {
            var _a = (0, tinycolor2_1.default)(litObj === null || litObj === void 0 ? void 0 : litObj.value).toRgb(), r = _a.r, g = _a.g, b = _a.b, a = _a.a;
            return {
                value: "rgba(".concat(r, ", ").concat(g, ", ").concat(b, ", ").concat(a, ")"),
            };
        }
    }
    function matchHSVColor() {
        return matchCall(tokens.hsvColor, convertHsv);
    }
    function matchColor() {
        return (matchHexColor() ||
            matchHSLColor() ||
            matchRGBAColor() ||
            matchRGBColor() ||
            matchLiteralColor() ||
            matchHSVColor());
    }
    function matchColorStop() {
        var _a;
        var color = matchColor();
        if (!color) {
            error('Expected color definition');
        }
        color.left = parseInt((_a = matchDistance()) === null || _a === void 0 ? void 0 : _a.value);
        return color;
    }
    function matchGradient(gradientType, pattern, orientationMatcher) {
        return matchCall(pattern, function () {
            var orientation = orientationMatcher();
            if (orientation) {
                if (!scan(tokens.comma)) {
                    error('Missing comma before color stops');
                }
            }
            return {
                type: gradientType,
                orientation: orientation,
                colorStops: matchListing(matchColorStop),
            };
        });
    }
    function matchLinearOrientation() {
        return matchSideOrCorner() || matchAngle();
    }
    function matchDefinition() {
        return (matchGradient('linear-gradient', tokens.linearGradient, matchLinearOrientation) ||
            matchGradient('repeating-linear-gradient', tokens.repeatingLinearGradient, matchLinearOrientation) ||
            matchGradient('radial-gradient', tokens.radialGradient, matchListRadialOrientations) ||
            matchGradient('repeating-radial-gradient', tokens.repeatingRadialGradient, matchListRadialOrientations));
    }
    function matchListDefinitions() {
        return matchListing(matchDefinition);
    }
    function getAST() {
        var _a;
        var ast = matchListDefinitions();
        if (input.length > 0) {
            error('Invalid input not EOF');
        }
        var ast0 = ast[0];
        var checkSelected = (_a = ast0 === null || ast0 === void 0 ? void 0 : ast0.colorStops) === null || _a === void 0 ? void 0 : _a.filter(function (c) {
            return (0, utils_js_1.isUpperCase)(c.value);
        }).length;
        var getGradientObj = function () {
            if (checkSelected > 0) {
                return ast0;
            }
            else {
                var val_1 = function (c, i) { return (i === 0 ? (0, formatters_js_1.high)(c) : (0, formatters_js_1.low)(c)); };
                return __assign(__assign({}, ast0), { colorStops: ast0.colorStops.map(function (c, i) { return (__assign(__assign({}, c), { value: val_1(c, i) })); }) });
            }
        };
        return getGradientObj();
    }
    function matchSideOrCorner() {
        return match('directional', tokens.sideOrCorner, 1);
    }
    function matchAngle() {
        return match('angular', tokens.angleValue, 1);
    }
    function matchListRadialOrientations() {
        var radialOrientations, radialOrientation = matchRadialOrientation(), lookaheadCache;
        if (radialOrientation) {
            radialOrientations = [];
            radialOrientations.push(radialOrientation);
            lookaheadCache = input;
            if (scan(tokens.comma)) {
                radialOrientation = matchRadialOrientation();
                if (radialOrientation) {
                    radialOrientations.push(radialOrientation);
                }
                else {
                    input = lookaheadCache;
                }
            }
        }
        return radialOrientations;
    }
    function matchRadialOrientation() {
        var radialType = matchCircle() || matchEllipse();
        if (radialType) {
            // @ts-expect-error - need to circle back for these types
            radialType.at = matchAtPosition();
        }
        else {
            var extent = matchExtentKeyword();
            if (extent) {
                radialType = extent;
                var positionAt = matchAtPosition();
                if (positionAt) {
                    // @ts-expect-error - need to circle back for these types
                    radialType.at = positionAt;
                }
            }
            else {
                var defaultPosition = matchPositioning();
                if (defaultPosition) {
                    radialType = {
                        type: 'default-radial',
                        // @ts-expect-error - need to circle back for these types
                        at: defaultPosition,
                    };
                }
            }
        }
        return radialType;
    }
    function matchLength() {
        return match('px', tokens.pixelValue, 1) || match('em', tokens.emValue, 1);
    }
    function matchCircle() {
        var circle = match('shape', /^(circle)/i, 0);
        if (circle) {
            // @ts-expect-error - need to circle back for these types
            circle.style = matchLength() || matchExtentKeyword();
        }
        return circle;
    }
    function matchEllipse() {
        var ellipse = match('shape', /^(ellipse)/i, 0);
        if (ellipse) {
            // @ts-expect-error - need to circle back for these types
            ellipse.style = matchDistance() || matchExtentKeyword();
        }
        return ellipse;
    }
    function matchExtentKeyword() {
        return match('extent-keyword', tokens.extentKeywords, 1);
    }
    function matchAtPosition() {
        if (match('position', /^at/, 0)) {
            var positioning = matchPositioning();
            if (!positioning) {
                error('Missing positioning value');
            }
            return positioning;
        }
    }
    function matchPositioning() {
        var location = matchCoordinates();
        if (location.x || location.y) {
            return {
                type: 'position',
                value: location,
            };
        }
    }
    function matchCoordinates() {
        return {
            x: matchDistance(),
            y: matchDistance(),
        };
    }
    function matchNumber() {
        return scan(tokens.number)[1];
    }
    var convertHsl = function (val) {
        var capIt = (0, utils_js_1.isUpperCase)(val === null || val === void 0 ? void 0 : val[0]);
        var hsl = matchListing(matchNumber);
        var _a = (0, tinycolor2_1.default)({
            h: hsl[0],
            s: hsl[1],
            l: hsl[2],
            a: hsl[3] || 1,
        }).toRgb(), r = _a.r, g = _a.g, b = _a.b, a = _a.a;
        return {
            value: "".concat(capIt ? 'RGBA' : 'rgba', "(").concat(r, ", ").concat(g, ", ").concat(b, ", ").concat(a, ")"),
        };
    };
    var convertHsv = function (val) {
        var capIt = (0, utils_js_1.isUpperCase)(val === null || val === void 0 ? void 0 : val[0]);
        var hsv = matchListing(matchNumber);
        var _a = (0, tinycolor2_1.default)({
            h: hsv[0],
            s: hsv[1],
            v: hsv[2],
            a: hsv[3] || 1,
        }).toRgb(), r = _a.r, g = _a.g, b = _a.b, a = _a.a;
        return {
            value: "".concat(capIt ? 'RGBA' : 'rgba', "(").concat(r, ", ").concat(g, ", ").concat(b, ", ").concat(a, ")"),
        };
    };
    var convertRgb = function (val) {
        var capIt = (0, utils_js_1.isUpperCase)(val === null || val === void 0 ? void 0 : val[0]);
        var captures = scan(tokens.spacedRgbColor);
        var _a = captures || __spreadArray([null], matchListing(matchNumber), true), r = _a[1], g = _a[2], b = _a[3], _b = _a[4], a = _b === void 0 ? 1 : _b;
        return {
            value: "".concat(capIt ? 'RGBA' : 'rgba', "(").concat(r, ", ").concat(g, ", ").concat(b, ", ").concat(a, ")"),
        };
    };
    function matchDistance() {
        return (match('%', tokens.percentageValue, 1) ||
            matchPositionKeyword() ||
            matchLength());
    }
    function matchPositionKeyword() {
        return match('position-keyword', tokens.positionKeywords, 1);
    }
    return getAST();
};
exports.gradientParser = gradientParser;
