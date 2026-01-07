import { memo, useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
var Portal = function (_a) {
    var _b;
    var children = _a.children;
    var id = 'id' + Math.random().toString(16).slice(2);
    var el = useRef((_b = document.getElementById(id)) !== null && _b !== void 0 ? _b : document.createElement('div'));
    var dynamic = useState(!el.current.parentElement)[0];
    useEffect(function () {
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
    return createPortal(children, el.current);
};
export default memo(Portal);
