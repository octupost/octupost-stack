import type { MessagesFormat } from './format/types.js';
export type Locale = string;
export type ExtractorMessage = {
    id: string;
    message: string;
    description?: string;
    references?: Array<{
        path: string;
    }>;
    /** Allows for additional properties like .po flags to be read and later written. */
    [key: string]: unknown;
};
export type MessagesConfig = {
    path: string;
    format: MessagesFormat;
    locales: 'infer' | ReadonlyArray<Locale>;
};
export type ExtractorConfig = {
    srcPath: string | Array<string>;
    sourceLocale: string;
    messages: MessagesConfig;
};
export type CatalogLoaderConfig = {
    messages: MessagesConfig;
};
