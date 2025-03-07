import clsx from 'clsx';
import { PropsWithChildren, ReactNode } from 'react'

export type PaneProps = PropsWithChildren<{
    title: string;
    menuHead?: ReactNode;
    id?: string;
    classContainer?: string;
    classHead?: string;
    classBody?: string;
}>
export default function Pane({
    title,
    menuHead,
    id,
    classContainer,
    classHead,
    classBody,
    children
}: PaneProps) {
    const props = id ? { id: id } : null
    return (
        <section
        {...props}
        className={clsx(
            "flex-1 items-center py-2 px-3 my-4 mx-auto border-2 rounded shadow-lg shadow-black/50 dark:shadow-zinc-50/50 tracking-wide",
            classContainer
        )}>
            <div 
            className={clsx(
                "flex flex-row justify-between items-center title-article-rose",
                classHead
            )}>
                <h2 className="uppercase">{title}</h2>
                {menuHead && (menuHead)}
            </div>

            <div className={clsx("space-y-3", classBody)}>
                {children}
            </div>
        </section>
    )
}