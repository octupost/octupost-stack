import { useEffect } from 'react';
import tinycolor from 'tinycolor2';
var usePaintHue = function (canvas, squareWidth) {
    useEffect(function () {
        var _a;
        var ctx = (_a = canvas === null || canvas === void 0 ? void 0 : canvas.current) === null || _a === void 0 ? void 0 : _a.getContext('2d', { willReadFrequently: true });
        if (ctx) {
            ctx.rect(0, 0, squareWidth, 14);
            var gradient = ctx.createLinearGradient(0, 0, squareWidth, 0);
            for (var i = 0; i <= 360; i += 30) {
                gradient.addColorStop(i / 360, "hsl(".concat(i, ", 100%, 50%)"));
            }
            ctx.fillStyle = gradient;
            ctx.fill();
        }
    }, [canvas, squareWidth]);
};
export default usePaintHue;
export var usePaintSat = function (canvas, h, l, squareWidth) {
    useEffect(function () {
        var _a;
        var ctx = (_a = canvas === null || canvas === void 0 ? void 0 : canvas.current) === null || _a === void 0 ? void 0 : _a.getContext('2d', { willReadFrequently: true });
        if (ctx) {
            ctx.rect(0, 0, squareWidth, 14);
            var gradient = ctx.createLinearGradient(0, 0, squareWidth, 0);
            for (var i = 0; i <= 100; i += 10) {
                gradient.addColorStop(i / 100, "hsl(".concat(h, ", ").concat(i, "%, ").concat(l, "%)"));
            }
            ctx.fillStyle = gradient;
            ctx.fill();
        }
    }, [canvas, h, l, squareWidth]);
};
export var usePaintLight = function (canvas, h, s, squareWidth) {
    useEffect(function () {
        var _a;
        var ctx = (_a = canvas === null || canvas === void 0 ? void 0 : canvas.current) === null || _a === void 0 ? void 0 : _a.getContext('2d', { willReadFrequently: true });
        if (ctx) {
            ctx.rect(0, 0, squareWidth, 14);
            var gradient = ctx.createLinearGradient(0, 0, squareWidth, 0);
            for (var i = 0; i <= 100; i += 10) {
                gradient.addColorStop(i / 100, "hsl(".concat(h, ", ").concat(s, "%, ").concat(i, "%)"));
            }
            ctx.fillStyle = gradient;
            ctx.fill();
        }
    }, [canvas, h, s, squareWidth]);
};
export var usePaintBright = function (canvas, h, s, squareWidth) {
    useEffect(function () {
        var _a;
        var ctx = (_a = canvas === null || canvas === void 0 ? void 0 : canvas.current) === null || _a === void 0 ? void 0 : _a.getContext('2d', { willReadFrequently: true });
        if (ctx) {
            ctx.rect(0, 0, squareWidth, 14);
            var gradient = ctx.createLinearGradient(0, 0, squareWidth, 0);
            for (var i = 0; i <= 100; i += 10) {
                var hsl = tinycolor({ h: h, s: s, v: i });
                gradient.addColorStop(i / 100, hsl.toHslString());
            }
            ctx.fillStyle = gradient;
            ctx.fill();
        }
    }, [canvas, h, s, squareWidth]);
};
