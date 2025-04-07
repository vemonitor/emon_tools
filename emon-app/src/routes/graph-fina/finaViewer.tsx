import { useParams } from "react-router";
import clsx from 'clsx';
import { GraphPane } from '@/components/layout/graph-pane';
import { FinaViewerList } from "./finaFilesViever";
import { ChartPane } from "./finaChartViever";
import { useState } from "react";
import { DataPath } from "../data-path/table-header-columns";
import { validateSlug } from "@/lib/utils";

type FinaViewerProps = {
  className?: string;
  slug?: string
}

export function FinaViewer({
  className,
  slug
}: FinaViewerProps) {
  const { path_slug } = useParams();
  const [selectedPath, setSelectedPath] = useState<DataPath | null>(null)
  const out_slug = validateSlug(slug)
  const selectedSlug = out_slug ? out_slug : path_slug
  return (
    <GraphPane
      title='Fina Files Viewer'
      listItems={<FinaViewerList
        selectedPath={selectedPath}
        setSelectedPath={setSelectedPath}
        path_slug={selectedSlug}
        classBody='h-full'
    />}
      chart={<ChartPane
        path_slug={selectedSlug ? selectedSlug : selectedPath?.slug}
        classBody='h-full'
      />}
      className={clsx('h-full', className)}
    />
  )
}