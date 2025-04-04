import clsx from 'clsx';
import { HostFeedViewerList } from './hostFeedsViever';
import { useParams } from 'react-router';
import { GraphPane } from '@/components/layout/graph-pane';
import { ChartFeedPane } from './hostedChartViever';
import { useState } from 'react';
import { EmonHost } from '../emon-host/table-header-columns';
import { validateSlug } from '@/lib/utils';

type HostedViewerProps = {
    slug?: string;
    className?: string;
}

export function HostedViewer({
    slug,
    className
}: HostedViewerProps) {
    const { host_slug } = useParams();
    const [selectedHost, setSelectedHost] = useState<EmonHost | null>(null)
    const out_slug = validateSlug(slug)
    const selectedSlug = out_slug ? out_slug : host_slug
    return (
        <GraphPane
            title='Emoncms Feeds Viewer'
            listItems={<HostFeedViewerList
                selectedHost={selectedHost}
                setSelectedHost={setSelectedHost}
                host_slug={selectedSlug}
                classBody='h-full'
            />}
            chart={<ChartFeedPane
                host_slug={selectedSlug ? selectedSlug : selectedHost?.slug}
                classBody='h-full'
            />}
            className={clsx('h-full', className)}
        />
    )
}

