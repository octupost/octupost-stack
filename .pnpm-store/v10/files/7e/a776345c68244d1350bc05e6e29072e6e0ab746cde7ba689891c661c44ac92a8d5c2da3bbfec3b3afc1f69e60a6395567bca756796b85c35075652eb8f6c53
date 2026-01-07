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
var react_1 = __importDefault(require("react"));
var context_js_1 = require("../context.js");
var formatters_js_1 = require("../utils/formatters.js");
var styles_js_1 = require("../styles/styles.js");
var icon_js_1 = __importStar(require("./icon.js"));
var GradientType = function () {
    var _a = (0, context_js_1.usePicker)(), gradientType = _a.gradientType, onChange = _a.onChange, value = _a.value, defaultStyles = _a.defaultStyles, pickerIdSuffix = _a.pickerIdSuffix;
    var isLinear = gradientType === 'linear-gradient';
    var isRadial = gradientType === 'radial-gradient';
    var handleLinear = function () {
        var remaining = value.split(/,(.+)/)[1];
        onChange("linear-gradient(90deg, ".concat(remaining));
    };
    var handleRadial = function () {
        var remaining = value.split(/,(.+)/)[1];
        onChange("radial-gradient(circle, ".concat(remaining));
    };
    return (react_1.default.createElement("div", { style: defaultStyles.rbgcpControlBtnWrapper },
        react_1.default.createElement("div", { onClick: handleLinear, id: "rbgcp-linear-btn".concat(pickerIdSuffix), 
            // className="rbgcp-control-icon-btn rbgcp-linear-btn"
            style: __assign(__assign({}, defaultStyles.rbgcpControlBtn), (isLinear && defaultStyles.rbgcpControlBtnSelected)), tabIndex: 0, role: "button", onKeyDown: function () {
                return;
            } },
            react_1.default.createElement(icon_js_1.LinearIcon, { color: isLinear ? '#568CF5' : '' })),
        react_1.default.createElement("div", { onClick: handleRadial, id: "rbgcp-radial-btn".concat(pickerIdSuffix), 
            // className="rbgcp-control-icon-btn rbgcp-radial-btn"
            style: __assign(__assign({}, defaultStyles.rbgcpControlBtn), (isRadial && defaultStyles.rbgcpControlBtnSelected)), tabIndex: 0, role: "button", onKeyDown: function () {
                return;
            } },
            react_1.default.createElement(icon_js_1.RadialIcon, { color: isRadial ? '#568CF5' : '' }))));
};
var StopPicker = function () {
    var _a = (0, context_js_1.usePicker)(), currentLeft = _a.currentLeft, currentColor = _a.currentColor, defaultStyles = _a.defaultStyles, handleGradient = _a.handleGradient, pickerIdSuffix = _a.pickerIdSuffix;
    var handleMove = function (newVal) {
        handleGradient(currentColor, (0, formatters_js_1.formatInputValues)(parseInt(newVal), 0, 100));
    };
    return (react_1.default.createElement("div", { 
        // className="rbgcp-stop-input-wrap"
        style: __assign(__assign(__assign(__assign({}, defaultStyles.rbgcpControlBtnWrapper), defaultStyles.rbgcpControlInputWrap), defaultStyles.rbgcpStopInputWrap), { paddingLeft: 8 }), id: "rbgcp-stop-input-wrapper".concat(pickerIdSuffix) },
        react_1.default.createElement(icon_js_1.StopIcon, null),
        react_1.default.createElement("input", { value: currentLeft, id: "rbgcp-stop-input".concat(pickerIdSuffix), onChange: function (e) { return handleMove(e.target.value); }, style: __assign(__assign({}, defaultStyles.rbgcpControlInput), defaultStyles.rbgcpStopInput) })));
};
var DegreePicker = function () {
    var _a = (0, context_js_1.usePicker)(), degrees = _a.degrees, onChange = _a.onChange, value = _a.value, defaultStyles = _a.defaultStyles, pickerIdSuffix = _a.pickerIdSuffix;
    var handleDegrees = function (e) {
        var newValue = (0, formatters_js_1.formatInputValues)(e.target.value, 0, 360);
        var remaining = value.split(/,(.+)/)[1];
        onChange("linear-gradient(".concat(newValue !== null && newValue !== void 0 ? newValue : 0, "deg, ").concat(remaining));
    };
    return (react_1.default.createElement("div", { 
        // className="rbgcp-degree-input-wrap"
        style: __assign(__assign(__assign({}, defaultStyles.rbgcpControlBtnWrapper), defaultStyles.rbgcpControlInputWrap), defaultStyles.rbgcpDegreeInputWrap), id: "rbgcp-degree-input-wrapper".concat(pickerIdSuffix) },
        react_1.default.createElement(icon_js_1.DegreesIcon, null),
        react_1.default.createElement("input", { value: degrees, onChange: function (e) { return handleDegrees(e); }, id: "rbgcp-degree-input".concat(pickerIdSuffix), 
            // className="rbgcp-control-input rbgcp-degree-input"
            style: __assign(__assign({}, defaultStyles.rbgcpControlInput), defaultStyles.rbgcpDegreeInput) }),
        react_1.default.createElement("div", { 
            // className="rbgcp-degree-circle-icon"
            style: __assign(__assign({}, defaultStyles.rbgcpDegreeIcon), { position: 'absolute', right: degrees > 99 ? 0 : degrees < 10 ? 7 : 3, top: 1, fontWeight: 400, fontSize: 13 }) }, "\u00B0")));
};
var DeleteBtn = function () {
    var _a = (0, context_js_1.usePicker)(), colors = _a.colors, selectedColor = _a.selectedColor, createGradientStr = _a.createGradientStr, defaultStyles = _a.defaultStyles, pickerIdSuffix = _a.pickerIdSuffix;
    var deletePoint = function () {
        if ((colors === null || colors === void 0 ? void 0 : colors.length) > 2) {
            var formatted = colors === null || colors === void 0 ? void 0 : colors.map(function (fc, i) { return (__assign(__assign({}, fc), { value: i === selectedColor - 1 ? (0, formatters_js_1.high)(fc) : (0, formatters_js_1.low)(fc) })); });
            var remaining = formatted === null || formatted === void 0 ? void 0 : formatted.filter(function (_, i) { return i !== selectedColor; });
            createGradientStr(remaining);
        }
    };
    return (react_1.default.createElement("div", { onClick: deletePoint, style: __assign(__assign({}, (0, styles_js_1.controlBtnStyles)(false, defaultStyles)), { width: 28 }), id: "rbgcp-point-delete-btn".concat(pickerIdSuffix), 
        // className="rbgcp-control-btn rbgcp-point-delete-btn"
        tabIndex: 0, role: "button", onKeyDown: function () {
            return;
        } },
        react_1.default.createElement(icon_js_1.default, null)));
};
var GradientControls = function (_a) {
    var hideGradientType = _a.hideGradientType, hideGradientAngle = _a.hideGradientAngle, hideGradientStop = _a.hideGradientStop;
    var _b = (0, context_js_1.usePicker)(), gradientType = _b.gradientType, defaultStyles = _b.defaultStyles, pickerIdSuffix = _b.pickerIdSuffix;
    return (react_1.default.createElement("div", { style: __assign(__assign({}, defaultStyles.rbgcpControlBtnWrapper), { marginTop: 12, marginBottom: -4, justifyContent: 'space-between', paddingLeft: hideGradientType ? 4 : 0 }), id: "rbgcp-gradient-controls-wrap".concat(pickerIdSuffix) },
        !hideGradientType && react_1.default.createElement(GradientType, null),
        react_1.default.createElement("div", { style: { width: 53 } }, !hideGradientAngle && gradientType === 'linear-gradient' && (react_1.default.createElement(DegreePicker, null))),
        !hideGradientStop && react_1.default.createElement(StopPicker, null),
        react_1.default.createElement(DeleteBtn, null)));
};
exports.default = GradientControls;
