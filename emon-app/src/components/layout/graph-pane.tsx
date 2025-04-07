import { Pane } from '@/components/layout/pane';
import clsx from 'clsx';
import {
    ResizableHandle,
    ResizablePanel,
    ResizablePanelGroup,
} from "@/components/ui/resizable"
import { ReactNode } from 'react';

type GraphPaneProps = {
    title: string;
    listItems: ReactNode;
    chart: ReactNode;
    className?: string;
}

export function GraphPane({
    title,
    listItems,
    chart,
    className
}: GraphPaneProps) {
    return (
        <Pane
            title={title}
            classBody={clsx('h-full', className)}
        >

            <ResizablePanelGroup
                direction="horizontal"
                className="min-h-[200px] w-full"
            >
                <ResizablePanel defaultSize={25} maxSize={40}>
                    <div className="flex h-full min-w-[350px] items-center justify-center p-2">
                        {listItems}
                    </div>
                </ResizablePanel>
                <ResizableHandle withHandle />
                <ResizablePanel defaultSize={75}>
                    <div className="flex h-full items-center justify-center p-2">
                        {chart}
                    </div>
                </ResizablePanel>
            </ResizablePanelGroup>
        </Pane>
    )
}