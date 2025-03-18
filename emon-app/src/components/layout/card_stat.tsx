import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from "@/components/ui/card"
import { PropsWithChildren, ReactNode } from "react";


export type ListBoxDataType = {
    count: number;
    size: string;
};

type CardStatListBoxProps = {
    title: string;
    data: ListBoxDataType;
}



export function CardStatListBox({
    title,
    data
}: CardStatListBoxProps) {
    return (
        <Card className="aspect-video">
            <CardHeader
                className="flex flex-col items-center justify-center p-2"
            >
                <CardTitle
                    className=""
                >{title}</CardTitle>
            </CardHeader>
            <CardContent
                className="flex flex-col items-center justify-center"
            >
                <div
                    className="text-5xl"
                >
                    {data.count}
                </div>
                <div
                    className="text-sm"
                >
                    {data.size}
                </div>
            </CardContent>
        </Card>
    )
}

type CardStatBoxProps = {
    title: string;
    value: string | number | boolean;
}

export function CardStatBox({
    title,
    value
}: CardStatBoxProps) {
    return (
        <Card className="aspect-video">
            <CardHeader
                className="flex flex-col items-center justify-center p-2"
            >
                <CardTitle>{title}</CardTitle>
            </CardHeader>
            <CardContent
                className="flex flex-col items-center justify-center text-5xl"
            >
                {value}
            </CardContent>
        </Card>
    )
}

type CardGroupBoxProps = PropsWithChildren & {
    title: string;
    children: ReactNode;
    description?: string;
    footer?: ReactNode;
    classHeader?: string;
    classTitle?: string;
    classDescription?: string;
    classContent?: string;
    classFooter?: string;
}

export function CardGroupBox({
    title,
    description,
    children,
    footer,
    classHeader,
    classTitle,
    classDescription,
    classContent,
    classFooter,
}: CardGroupBoxProps) {
    return (
        <Card className="aspect-video">
            <CardHeader
                className={classHeader}
            >
                <CardTitle
                    className={classTitle}
                >{title}</CardTitle>
                {description && (
                    <CardDescription
                        className={classDescription}
                    >{description}</CardDescription>
                )}
            </CardHeader>
            <CardContent
                className={classContent}
            >
                {children}
            </CardContent>
            {footer && (
                <CardFooter className={classFooter}>
                    {footer}
                </CardFooter>
            )}
        </Card>
    )
}
