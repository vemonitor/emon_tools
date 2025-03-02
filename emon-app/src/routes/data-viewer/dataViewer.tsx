import Pane from '../../components/layout/pane'
import { ChartPane } from './finaChartViever';
import { DataViewerList } from './finaFilesViever';
import { useNavigate, useParams } from "react-router";
import { useAuth } from '@/hooks/use-auth';
import { useEffect } from 'react';
import clsx from 'clsx';


export function DataViewer({
  className
}: {
  className?: string
}) {
  const { source_ref } = useParams();
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isAuthenticated) {
      navigate("/login");
    }
  }, [isAuthenticated, navigate]);
  return (
    <Pane
      title='Fina Reader'
      classBody={clsx('h-full', className)}
    >
      
      <div className='grid grid-cols-8 h-full'>
        <div className='col-span-2 h-full'>
          <DataViewerList 
            source={source_ref ?? 'archive'}
          />
        </div>
        <div className='col-span-6 h-full'>
          <ChartPane
            source={source_ref ?? 'archive'}
            classBody='h-full'
          />
        </div>
      </div>
    </Pane>
  )
}

