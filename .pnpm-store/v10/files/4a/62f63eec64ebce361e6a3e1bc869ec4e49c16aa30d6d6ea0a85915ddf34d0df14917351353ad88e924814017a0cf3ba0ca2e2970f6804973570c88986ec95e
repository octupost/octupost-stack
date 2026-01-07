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
import { darkStyles } from './darkStyles.js';
var styles = {
    body: {
        boxSizing: 'border-box',
        background: 'rgb(255, 255, 255)',
    },
    rbgcpControlBtn: {
        paddingLeft: '8px',
        paddingRight: '8px',
        lineHeight: '1',
        borderRadius: '4px',
        fontWeight: 700,
        fontSize: '12px',
        height: '24px',
        transition: 'all 160ms ease',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'rgba(255, 255, 255, 0)',
        boxShadow: '1px 1px 3px rgba(0, 0, 0, 0)',
        color: 'rgb(86, 86, 86)',
    },
    rbgcpControlIcon: {
        stroke: 'rgb(50, 49, 54)',
    },
    rbgcpControlIconBtn: {
        width: '30px',
        height: '24px',
        borderRadius: '4px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative',
    },
    rbgcpControlBtnWrapper: {
        height: '28px',
        background: '#e9e9f5',
        borderRadius: '6px',
        padding: '2px',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        position: 'relative',
    },
    rbgcpColorModelDropdown: {
        position: 'absolute',
        right: '-2px',
        top: '34px',
        padding: '5px',
        background: '#e9e9f5',
        zIndex: 100000000,
        borderRadius: '6px',
        boxShadow: '1px 1px 14px 1px rgba(0, 0, 0, 0.25)',
    },
    rbgcpEyedropperCover: {
        position: 'fixed',
        left: '0px',
        top: '0px',
        zIndex: 100000000,
        width: '100vw',
        height: '100vh',
        cursor: 'copy',
    },
    rbgcpControlInput: {
        height: '24px',
        borderRadius: '4px',
        border: 'none',
        outline: 'none',
        textAlign: 'center',
        width: '34px',
        fontWeight: 500,
        color: 'rgb(50, 49, 54)',
        fontSize: '13px',
        background: 'transparent',
    },
    rbgcpInputLabel: {
        textAlign: 'center',
        lineHeight: '1.2',
        fontWeight: 700,
        color: 'rgb(86, 86, 86)',
        fontSize: '11px',
    },
    rbgcpInput: {
        height: '32px',
        borderRadius: '6px',
        border: '1px solid #bebebe',
        width: '100%',
        padding: '2px',
        outline: 'none',
        color: 'black',
        fontWeight: 400,
        textAlign: 'center',
        background: 'transparent',
        fontSize: '15px',
    },
    rbgcpHandle: {
        position: 'absolute',
        border: '2px solid white',
        borderRadius: '50%',
        boxShadow: '0px 0px 3px rgba(0, 0, 0, 0.5)',
        width: '18px',
        height: '18px',
        zIndex: 1000,
        transition: 'all 30ms linear',
        boxSizing: 'border-box',
        willChange: 'transform',
        outline: 'none',
    },
    rbgcpCanvasWrapper: {
        borderRadius: '6px',
        overflow: 'hidden',
        height: '294px',
    },
    rbgcpCheckered: {
        background: "linear-gradient(\n      45deg,\n      rgba(0, 0, 0, 0.18) 25%,\n      transparent 25%,\n      transparent 75%,\n      rgba(0, 0, 0, 0.18) 75%,\n      rgba(0, 0, 0, 0.18) 0\n    ),\n    linear-gradient(\n      45deg,\n      rgba(0, 0, 0, 0.18) 25%,\n      transparent 25%,\n      transparent 75%,\n      rgba(0, 0, 0, 0.18) 75%,\n      rgba(0, 0, 0, 0.18) 0\n    ),\n    white",
        backgroundRepeat: 'repeat, repeat',
        backgroundPosition: '0px 0, 7px 7px',
        transformOrigin: '0 0 0',
        backgroundOrigin: 'padding-box, padding-box',
        backgroundClip: 'border-box, border-box',
        backgroundSize: '14px 14px, 14px 14px',
        boxShadow: 'none',
        textShadow: 'none',
        transition: 'none',
        transform: 'scaleX(1) scaleY(1) scaleZ(1)',
        borderRadius: '10px',
    },
    rbgcpOpacityOverlay: {
        position: 'absolute',
        left: '0px',
        top: '0px',
        width: '100%',
        height: '100%',
        borderRadius: '10px',
    },
    rbgcpGradientHandleWrap: {
        position: 'absolute',
        zIndex: 10000,
        top: '-2px',
        outline: 'none',
    },
    rbgcpGradientHandle: {
        border: '2px solid white',
        borderRadius: '50%',
        boxShadow: '0px 0px 3px rgba(0, 0, 0, 0.5)',
        width: '18px',
        height: '18px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
    },
    rbgcpControlIcon2: {
        fill: '#323136',
    },
    rbgcpControlBtnSelected: {
        background: 'white',
        color: '#568cf5',
        boxShadow: '1px 1px 3px rgba(0, 0, 0, 0.2)',
    },
    rbgcpComparibleLabel: {
        color: '#323136',
    }
};
export var getStyles = function (isDarkMode, passedStyles) {
    var mergedStyles = __assign({}, styles);
    if (isDarkMode) {
        for (var key in darkStyles) {
            if (Object.prototype.hasOwnProperty.call(darkStyles, key)) {
                ;
                mergedStyles[key] = __assign(__assign({}, (Object.prototype.hasOwnProperty.call(mergedStyles, key)
                    ? mergedStyles[key]
                    : {})), darkStyles[key]);
            }
        }
    }
    for (var key in passedStyles) {
        if (Object.prototype.hasOwnProperty.call(passedStyles, key)) {
            ;
            mergedStyles[key] = __assign(__assign({}, (Object.prototype.hasOwnProperty.call(mergedStyles, key)
                ? mergedStyles[key]
                : {})), passedStyles[key]);
        }
    }
    return mergedStyles;
};
export var colorTypeBtnStyles = function (selected, styles) {
    if (selected) {
        return __assign(__assign({}, styles.rbgcpControlBtn), styles.rbgcpControlBtnSelected);
    }
    else {
        return __assign({}, styles.rbgcpControlBtn);
    }
};
export var controlBtnStyles = function (selected, styles) {
    if (selected) {
        return __assign(__assign({}, styles.rbgcpControlIconBtn), styles.rbgcpControlBtnSelected);
    }
    else {
        return __assign({}, styles.rbgcpControlIconBtn);
    }
};
export var modalBtnStyles = function (selected, styles) {
    if (selected) {
        return __assign(__assign(__assign({}, styles.rbgcpControlBtn), styles.rbgcpColorModelDropdownBtn), styles.rbgcpControlBtnSelected);
    }
    else {
        return __assign(__assign({}, styles.rbgcpControlBtn), styles.rbgcpColorModelDropdownBtn);
    }
};
