// Essentialls lodash/set, but we avoid this dependency
function setNestedProperty(obj, keyPath, value) {
  const keys = keyPath.split('.');
  let current = obj;
  for (let i = 0; i < keys.length - 1; i++) {
    const key = keys[i];
    if (!(key in current) || typeof current[key] !== 'object' || current[key] === null) {
      current[key] = {};
    }
    current = current[key];
  }
  current[keys[keys.length - 1]] = value;
}
function getSortedMessages(messages) {
  return messages.toSorted((messageA, messageB) => {
    const pathA = messageA.references?.[0]?.path ?? '';
    const pathB = messageB.references?.[0]?.path ?? '';
    if (pathA === pathB) {
      return localeCompare(messageA.id, messageB.id);
    } else {
      return localeCompare(pathA, pathB);
    }
  });
}
function localeCompare(a, b) {
  return a.localeCompare(b, 'en');
}
function getDefaultProjectRoot() {
  return process.cwd();
}

export { getDefaultProjectRoot, getSortedMessages, localeCompare, setNestedProperty };
