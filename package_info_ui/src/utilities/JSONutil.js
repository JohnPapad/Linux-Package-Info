export const downloadJSON = (data) => {
    if (!data) return;
    const link = document.createElement('a');
    const filename = 'packages.json';

    const href = `data:text/json;charset=utf-8, ${encodeURIComponent(
        JSON.stringify(data)
    )}`;

    link.setAttribute('href', href);
    link.setAttribute('download', filename);
    link.click();
}