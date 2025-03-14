function generateTimestamp() {
    let now = new Date();
    let datePart = now.toISOString().split('T')[0].replace(/-/g, ''); // YYYYMMDD
    let timePart = now.toTimeString().split(' ')[0].replace(/:/g, ''); // HHMMSS

    let microseconds = String(Math.floor((performance.now() % 1) * 1000000)).padStart(6, '0');

    return `${datePart}_${timePart}_${microseconds}`;
}