"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var react_1 = require("react");
var react_dom_1 = require("react-dom");
var Portal = function (_a) {
    var _b;
    var children = _a.children;
    var id = 'id' + Math.random().toString(16).slice(2);
    var el = (0, react_1.useRef)((_b = document.getElementById(id)) !== null && _b !== void 0 ? _b : document.createElement('div'));
    var dynamic = (0, react_1.useState)(!el.current.parentElement)[0];
    (0, react_1.useEffect)(function () {
        var refValue = el.current;
        if (dynamic) {
            el.current.id = id;
            document.body.appendChild(el.current);
        }
        return function () {
            if (dynamic && refValue.parentElement) {
                refValue.parentElement.removeChild(refValue);
            }
        };
        //eslint-disable-next-line
    }, [id]);
    return (0, react_dom_1.createPortal)(children, el.current);
};
exports.default = (0, react_1.memo)(Portal);
