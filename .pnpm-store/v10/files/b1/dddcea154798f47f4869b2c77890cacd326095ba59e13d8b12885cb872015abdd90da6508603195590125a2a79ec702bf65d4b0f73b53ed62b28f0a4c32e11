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
import { usePicker } from '../context.js';
import { formatInputValues, low, high } from '../utils/formatters.js';
import { controlBtnStyles } from '../styles/styles.js';
import TrashIcon, { LinearIcon, RadialIcon, DegreesIcon, StopIcon, } from './icon.js';
var GradientType = function () {
    var _a = usePicker(), gradientType = _a.gradientType, onChange = _a.onChange, value = _a.value, defaultStyles = _a.defaultStyles, pickerIdSuffix = _a.pickerIdSuffix;
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
    return (React.createElement("div", { style: defaultStyles.rbgcpControlBtnWrapper },
        React.createElement("div", { onClick: handleLinear, id: "rbgcp-linear-btn".concat(pickerIdSuffix), 
            // className="rbgcp-control-icon-btn rbgcp-linear-btn"
            style: __assign(__assign({}, defaultStyles.rbgcpControlBtn), (isLinear && defaultStyles.rbgcpControlBtnSelected)), tabIndex: 0, role: "button", onKeyDown: function () {
                return;
            } },
            React.createElement(LinearIcon, { color: isLinear ? '#568CF5' : '' })),
        React.createElement("div", { onClick: handleRadial, id: "rbgcp-radial-btn".concat(pickerIdSuffix), 
            // className="rbgcp-control-icon-btn rbgcp-radial-btn"
            style: __assign(__assign({}, defaultStyles.rbgcpControlBtn), (isRadial && defaultStyles.rbgcpControlBtnSelected)), tabIndex: 0, role: "button", onKeyDown: function () {
                return;
            } },
            React.createElement(RadialIcon, { color: isRadial ? '#568CF5' : '' }))));
};
var StopPicker = function () {
    var _a = usePicker(), currentLeft = _a.currentLeft, currentColor = _a.currentColor, defaultStyles = _a.defaultStyles, handleGradient = _a.handleGradient, pickerIdSuffix = _a.pickerIdSuffix;
    var handleMove = function (newVal) {
        handleGradient(currentColor, formatInputValues(parseInt(newVal), 0, 100));
    };
    return (React.createElement("div", { 
        // className="rbgcp-stop-input-wrap"
        style: __assign(__assign(__assign(__assign({}, defaultStyles.rbgcpControlBtnWrapper), defaultStyles.rbgcpControlInputWrap), defaultStyles.rbgcpStopInputWrap), { paddingLeft: 8 }), id: "rbgcp-stop-input-wrapper".concat(pickerIdSuffix) },
        React.createElement(StopIcon, null),
        React.createElement("input", { value: currentLeft, id: "rbgcp-stop-input".concat(pickerIdSuffix), onChange: function (e) { return handleMove(e.target.value); }, style: __assign(__assign({}, defaultStyles.rbgcpControlInput), defaultStyles.rbgcpStopInput) })));
};
var DegreePicker = function () {
    var _a = usePicker(), degrees = _a.degrees, onChange = _a.onChange, value = _a.value, defaultStyles = _a.defaultStyles, pickerIdSuffix = _a.pickerIdSuffix;
    var handleDegrees = function (e) {
        var newValue = formatInputValues(e.target.value, 0, 360);
        var remaining = value.split(/,(.+)/)[1];
        onChange("linear-gradient(".concat(newValue !== null && newValue !== void 0 ? newValue : 0, "deg, ").concat(remaining));
    };
    return (React.createElement("div", { 
        // className="rbgcp-degree-input-wrap"
        style: __assign(__assign(__assign({}, defaultStyles.rbgcpControlBtnWrapper), defaultStyles.rbgcpControlInputWrap), defaultStyles.rbgcpDegreeInputWrap), id: "rbgcp-degree-input-wrapper".concat(pickerIdSuffix) },
        React.createElement(DegreesIcon, null),
        React.createElement("input", { value: degrees, onChange: function (e) { return handleDegrees(e); }, id: "rbgcp-degree-input".concat(pickerIdSuffix), 
            // className="rbgcp-control-input rbgcp-degree-input"
            style: __assign(__assign({}, defaultStyles.rbgcpControlInput), defaultStyles.rbgcpDegreeInput) }),
        React.createElement("div", { 
            // className="rbgcp-degree-circle-icon"
            style: __assign(__assign({}, defaultStyles.rbgcpDegreeIcon), { position: 'absolute', right: degrees > 99 ? 0 : degrees < 10 ? 7 : 3, top: 1, fontWeight: 400, fontSize: 13 }) }, "\u00B0")));
};
var DeleteBtn = function () {
    var _a = usePicker(), colors = _a.colors, selectedColor = _a.selectedColor, createGradientStr = _a.createGradientStr, defaultStyles = _a.defaultStyles, pickerIdSuffix = _a.pickerIdSuffix;
    var deletePoint = function () {
        if ((colors === null || colors === void 0 ? void 0 : colors.length) > 2) {
            var formatted = colors === null || colors === void 0 ? void 0 : colors.map(function (fc, i) { return (__assign(__assign({}, fc), { value: i === selectedColor - 1 ? high(fc) : low(fc) })); });
            var remaining = formatted === null || formatted === void 0 ? void 0 : formatted.filter(function (_, i) { return i !== selectedColor; });
            createGradientStr(remaining);
        }
    };
    return (React.createElement("div", { onClick: deletePoint, style: __assign(__assign({}, controlBtnStyles(false, defaultStyles)), { width: 28 }), id: "rbgcp-point-delete-btn".concat(pickerIdSuffix), 
        // className="rbgcp-control-btn rbgcp-point-delete-btn"
        tabIndex: 0, role: "button", onKeyDown: function () {
            return;
        } },
        React.createElement(TrashIcon, null)));
};
var GradientControls = function (_a) {
    var hideGradientType = _a.hideGradientType, hideGradientAngle = _a.hideGradientAngle, hideGradientStop = _a.hideGradientStop;
    var _b = usePicker(), gradientType = _b.gradientType, defaultStyles = _b.defaultStyles, pickerIdSuffix = _b.pickerIdSuffix;
    return (React.createElement("div", { style: __assign(__assign({}, defaultStyles.rbgcpControlBtnWrapper), { marginTop: 12, marginBottom: -4, justifyContent: 'space-between', paddingLeft: hideGradientType ? 4 : 0 }), id: "rbgcp-gradient-controls-wrap".concat(pickerIdSuffix) },
        !hideGradientType && React.createElement(GradientType, null),
        React.createElement("div", { style: { width: 53 } }, !hideGradientAngle && gradientType === 'linear-gradient' && (React.createElement(DegreePicker, null))),
        !hideGradientStop && React.createElement(StopPicker, null),
        React.createElement(DeleteBtn, null)));
};
export default GradientControls;
