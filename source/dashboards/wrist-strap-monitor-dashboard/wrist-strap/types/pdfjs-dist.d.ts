// In types/pdfjs-dist.d.ts (or a similar .d.ts file like env.d.ts)

declare module 'pdfjs-dist/build/pdf.mjs' {
    const pdfjsLib: any; // You can be more specific if you know the structure
    export = pdfjsLib;
    export * from 'pdfjs-dist'; // This attempts to re-export existing types if available from the main package
}

declare module 'pdfjs-dist/build/pdf.worker.min.mjs?url' {
    const workerSrc: string;
    export default workerSrc;
}