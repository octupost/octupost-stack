/* eslint-disable react/no-array-index-key */
/* eslint-disable jsx-a11y/no-static-element-interactions */
import React from 'react';
import { usePicker } from '../context.js';
import { fakePresets } from '../constants.js';
var Presets = function (_a) {
    var _b = _a.presets, presets = _b === void 0 ? [] : _b;
    var _c = usePicker(), value = _c.value, onChange = _c.onChange, isDarkMode = _c.isDarkMode, squareWidth = _c.squareWidth, handleChange = _c.handleChange, pickerIdSuffix = _c.pickerIdSuffix;
    var getPresets = function () {
        if ((presets === null || presets === void 0 ? void 0 : presets.length) > 0) {
            return presets === null || presets === void 0 ? void 0 : presets.slice(0, 18);
        }
        else {
            return fakePresets;
        }
    };
    var handlePresetClick = function (preset) {
        if (preset === null || preset === void 0 ? void 0 : preset.includes('gradient')) {
            onChange(preset);
        }
        else {
            handleChange(preset);
        }
    };
    var getBorder = function (p) {
        if (!p || isDarkMode)
            return '';
        var c = p === null || p === void 0 ? void 0 : p.replace(' ', '');
        if (c === 'rgba(255,255,255,1)') {
            return '1px solid #96959c';
        }
        return '';
    };
    return (React.createElement("div", { style: {
            marginTop: 14,
            display: 'flex',
            justifyContent: 'space-between',
        }, id: "rbgcp-footer-wrapper".concat(pickerIdSuffix) },
        React.createElement("div", { style: {
                width: 50,
                height: 50,
                flexShrink: 0,
                borderRadius: 6,
                background: value,
                border: getBorder(value),
            }, id: "rbgcp-preview".concat(pickerIdSuffix) }),
        React.createElement("div", { style: {
                rowGap: 3,
                display: 'flex',
                flexWrap: 'wrap',
                width: squareWidth - 57,
                justifyContent: 'space-between',
            }, id: "rbgcp-presets-wrapper".concat(pickerIdSuffix) }, getPresets().map(function (p, key) { return (React.createElement("div", { key: "".concat(p, "-").concat(key), id: "rbgcp-preset-".concat(key, "-wrapper").concat(pickerIdSuffix), style: { width: "calc(100% / 9)", paddingLeft: 3 } },
            React.createElement("div", { style: {
                    height: 23.5,
                    width: '100%',
                    background: p,
                    borderRadius: 4,
                    border: getBorder(p),
                }, 
                // className="rbgcp-preset-color"
                onClick: function () { return handlePresetClick(p); }, id: "rbgcp-preset-".concat(key).concat(pickerIdSuffix) }))); }))));
};
export default Presets;
