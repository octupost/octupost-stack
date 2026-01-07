"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
var react_1 = __importDefault(require("react"));
var Hue_js_1 = __importDefault(require("./Hue.js"));
var Inputs_js_1 = __importDefault(require("./Inputs.js"));
var Square_js_1 = __importDefault(require("./Square.js"));
var Opacity_js_1 = __importDefault(require("./Opacity.js"));
var Presets_js_1 = __importDefault(require("./Presets.js"));
var Controls_js_1 = __importDefault(require("./Controls.js"));
var context_js_1 = require("../context.js");
var GradientBar_js_1 = __importDefault(require("./GradientBar.js"));
var Picker = function (_a) {
    var locales = _a.locales, presets = _a.presets, hideHue = _a.hideHue, hideInputs = _a.hideInputs, hidePresets = _a.hidePresets, hideOpacity = _a.hideOpacity, hideEyeDrop = _a.hideEyeDrop, hideControls = _a.hideControls, hideInputType = _a.hideInputType, hideColorGuide = _a.hideColorGuide, hidePickerSquare = _a.hidePickerSquare, hideGradientType = _a.hideGradientType, hideGradientStop = _a.hideGradientStop, hideGradientAngle = _a.hideGradientAngle, hideColorTypeBtns = _a.hideColorTypeBtns, hideAdvancedSliders = _a.hideAdvancedSliders, hideGradientControls = _a.hideGradientControls;
    var _b = (0, context_js_1.usePicker)(), isGradient = _b.isGradient, pickerIdSuffix = _b.pickerIdSuffix;
    return (react_1.default.createElement("div", { style: { userSelect: 'none' }, id: "rbgcp-color-picker".concat(pickerIdSuffix) },
        !hidePickerSquare && react_1.default.createElement(Square_js_1.default, null),
        !hideControls && (react_1.default.createElement(Controls_js_1.default, { locales: locales, hideEyeDrop: hideEyeDrop, hideInputType: hideInputType, hideColorGuide: hideColorGuide, hideGradientType: hideGradientType, hideGradientStop: hideGradientStop, hideColorTypeBtns: hideColorTypeBtns, hideGradientAngle: hideGradientAngle, hideAdvancedSliders: hideAdvancedSliders, hideGradientControls: hideGradientControls })),
        isGradient && react_1.default.createElement(GradientBar_js_1.default, null),
        !hideHue && react_1.default.createElement(Hue_js_1.default, null),
        !hideOpacity && react_1.default.createElement(Opacity_js_1.default, null),
        !hideInputs && react_1.default.createElement(Inputs_js_1.default, null),
        !hidePresets && react_1.default.createElement(Presets_js_1.default, { presets: presets })));
};
exports.default = Picker;
