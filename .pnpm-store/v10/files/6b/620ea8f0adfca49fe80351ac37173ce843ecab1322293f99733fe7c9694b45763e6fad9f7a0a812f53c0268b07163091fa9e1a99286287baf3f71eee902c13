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
var ComparibleColors = function (_a) {
    var openComparibles = _a.openComparibles;
    var _b = usePicker(), tinyColor = _b.tinyColor, handleChange = _b.handleChange, defaultStyles = _b.defaultStyles, pickerIdSuffix = _b.pickerIdSuffix;
    var analogous = tinyColor.analogous();
    var monochromatic = tinyColor.monochromatic();
    var triad = tinyColor.triad();
    var tetrad = tinyColor.tetrad();
    var handleClick = function (tiny) {
        var _a = tiny.toRgb(), r = _a.r, g = _a.g, b = _a.b, a = _a.a;
        handleChange("rgba(".concat(r, ",").concat(g, ",").concat(b, ",").concat(a, ")"));
    };
    return (React.createElement("div", { style: {
            width: '100%',
            transition: 'all 120ms linear',
            height: openComparibles ? 216 : 0,
        }, id: "rbgcp-comparible-colors-wrapper".concat(pickerIdSuffix) },
        React.createElement("div", { style: {
                paddingTop: 11,
                display: openComparibles ? '' : 'none',
                position: 'relative',
            }, id: "rbgcp-comparible-colors-inner".concat(pickerIdSuffix) },
            React.createElement("div", { style: __assign({ textAlign: 'center', fontSize: 13, fontWeight: 600, position: 'absolute', top: 6.5, left: 2 }, defaultStyles.rbgcpComparibleLabel), id: "rbgcp-comparible-color-guide-label".concat(pickerIdSuffix) }, "Color Guide"),
            React.createElement("div", { style: __assign({ textAlign: 'center', fontSize: 12, fontWeight: 500, marginTop: 3 }, defaultStyles.rbgcpComparibleLabel), id: "rbgcp-comparible-analogous-colors-label".concat(pickerIdSuffix) }, "Analogous"),
            React.createElement("div", { style: { borderRadius: 5, overflow: 'hidden', display: 'flex' }, id: "rbgcp-comparible-analogous-colors".concat(pickerIdSuffix) }, analogous === null || analogous === void 0 ? void 0 : analogous.map(function (c, key) { return (React.createElement("div", { key: key, id: "rbgcp-comparible-analogous-color-".concat(key).concat(pickerIdSuffix), style: { width: '20%', height: 30, background: c.toHexString() }, onClick: function () { return handleClick(c); } })); })),
            React.createElement("div", { style: __assign({ textAlign: 'center', fontSize: 12, fontWeight: 500, marginTop: 3 }, defaultStyles.rbgcpComparibleLabel), id: "rbgcp-comparible-monochromatic-colors-label".concat(pickerIdSuffix) }, "Monochromatic"),
            React.createElement("div", { style: {
                    borderRadius: 5,
                    overflow: 'hidden',
                    display: 'flex',
                    justifyContent: 'flex-end',
                }, id: "rbgcp-comparible-monochromatic-colors".concat(pickerIdSuffix) }, monochromatic === null || monochromatic === void 0 ? void 0 : monochromatic.map(function (c, key) { return (React.createElement("div", { key: key, id: "rbgcp-comparible-monochromatic-color-".concat(key).concat(pickerIdSuffix), style: { width: '20%', height: 30, background: c.toHexString() }, onClick: function () { return handleClick(c); } })); })),
            React.createElement("div", { style: __assign({ textAlign: 'center', fontSize: 12, fontWeight: 500, marginTop: 3 }, defaultStyles.rbgcpComparibleLabel), id: "rbgcp-comparible-triad-colors-label".concat(pickerIdSuffix) }, "Triad"),
            React.createElement("div", { style: {
                    borderRadius: 5,
                    overflow: 'hidden',
                    display: 'flex',
                    justifyContent: 'flex-end',
                }, id: "rbgcp-comparible-triad-colors".concat(pickerIdSuffix) }, triad === null || triad === void 0 ? void 0 : triad.map(function (c, key) { return (React.createElement("div", { key: key, id: "rbgcp-comparible-triad-color-".concat(key).concat(pickerIdSuffix), style: {
                    width: 'calc(100% / 3)',
                    height: 28,
                    background: c.toHexString(),
                }, onClick: function () { return handleClick(c); } })); })),
            React.createElement("div", { style: __assign({ textAlign: 'center', fontSize: 12, fontWeight: 500, marginTop: 3 }, defaultStyles.rbgcpComparibleLabel), id: "rbgcp-comparible-tetrad-colors-label".concat(pickerIdSuffix) }, "Tetrad"),
            React.createElement("div", { style: {
                    borderRadius: 5,
                    overflow: 'hidden',
                    display: 'flex',
                    justifyContent: 'flex-end',
                }, id: "rbgcp-comparible-tetrad-colors".concat(pickerIdSuffix) }, tetrad === null || tetrad === void 0 ? void 0 : tetrad.map(function (c, key) { return (React.createElement("div", { key: key, id: "rbgcp-comparible-tetrad-color-".concat(key).concat(pickerIdSuffix), style: { width: '25%', height: 28, background: c.toHexString() }, onClick: function () { return handleClick(c); } })); })))));
};
export default ComparibleColors;
