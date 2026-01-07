import React from 'react';
import Hue from './Hue.js';
import Inputs from './Inputs.js';
import Square from './Square.js';
import Opacity from './Opacity.js';
import Presets from './Presets.js';
import Controls from './Controls.js';
import { usePicker } from '../context.js';
import GradientBar from './GradientBar.js';
var Picker = function (_a) {
    var locales = _a.locales, presets = _a.presets, hideHue = _a.hideHue, hideInputs = _a.hideInputs, hidePresets = _a.hidePresets, hideOpacity = _a.hideOpacity, hideEyeDrop = _a.hideEyeDrop, hideControls = _a.hideControls, hideInputType = _a.hideInputType, hideColorGuide = _a.hideColorGuide, hidePickerSquare = _a.hidePickerSquare, hideGradientType = _a.hideGradientType, hideGradientStop = _a.hideGradientStop, hideGradientAngle = _a.hideGradientAngle, hideColorTypeBtns = _a.hideColorTypeBtns, hideAdvancedSliders = _a.hideAdvancedSliders, hideGradientControls = _a.hideGradientControls;
    var _b = usePicker(), isGradient = _b.isGradient, pickerIdSuffix = _b.pickerIdSuffix;
    return (React.createElement("div", { style: { userSelect: 'none' }, id: "rbgcp-color-picker".concat(pickerIdSuffix) },
        !hidePickerSquare && React.createElement(Square, null),
        !hideControls && (React.createElement(Controls, { locales: locales, hideEyeDrop: hideEyeDrop, hideInputType: hideInputType, hideColorGuide: hideColorGuide, hideGradientType: hideGradientType, hideGradientStop: hideGradientStop, hideColorTypeBtns: hideColorTypeBtns, hideGradientAngle: hideGradientAngle, hideAdvancedSliders: hideAdvancedSliders, hideGradientControls: hideGradientControls })),
        isGradient && React.createElement(GradientBar, null),
        !hideHue && React.createElement(Hue, null),
        !hideOpacity && React.createElement(Opacity, null),
        !hideInputs && React.createElement(Inputs, null),
        !hidePresets && React.createElement(Presets, { presets: presets })));
};
export default Picker;
