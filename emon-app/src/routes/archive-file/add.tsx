import { AddActionType } from "@/lib/types";
import { ArchiveFileForm, ArchiveFileFormType } from "./form";
import { useAuth } from "@/hooks/use-auth";
import { useNavigate } from "react-router";
import { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";

const AddArchiveFileAction = async(
  values: ArchiveFileFormType,
  fetchWithAuth: (input: RequestInfo, init?: RequestInit) => Promise<Response>
): AddActionType => {
  

  const data = {
      ...values,
      id: undefined
  }

  try {
    const response = await fetchWithAuth(
      `http://127.0.0.1:8000/api/v1/archive_file/add/`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      }
    ).then((response) => response.json())
    if (!response.success) {
      return {
        success: false,
        msg: response.msg,
        errors: response.errors,
        from_error: response.from_error,
      }
    }
  } catch (error: unknown) {
    console.log('Error fetching data:', error);
    return {
      success: false,
      msg: 'Unable to save data, please control all fields',
      error: error instanceof Error ? error.message : 'Unknown error'
    }
  }

  return {success: true, redirect: `/archive-file`};
};

function AddArchiveFile() {
  const { isAuthenticated, fetchWithAuth } = useAuth();
  
  const navigate = useNavigate();
  useEffect(() => {
    if (!isAuthenticated) {
      navigate("/login");
    }
  }, [isAuthenticated, navigate]);
  
  const archiveGroups = useQuery(
    {
      queryKey: ['archive_group'],
      retry: false,
      refetchOnMount: 'always',  // Always refetch when the component mounts
      queryFn: () =>
        fetchWithAuth(
          `http://127.0.0.1:8000/api/v1/archive_group/`,
          {
            method: 'GET',
          }
        ).then((response) => response.json()),
    }
  );

  const emonHosts = useQuery(
    {
      queryKey: ['emon_host'],
      retry: false,
      refetchOnMount: 'always',  // Always refetch when the component mounts
      queryFn: () =>
        fetchWithAuth(
          `http://127.0.0.1:8000/api/v1/emon_host/`,
          {
            method: 'GET',
          }
        ).then((response) => response.json()),
    }
  );

  return (
    <div>
      {archiveGroups.isPending || emonHosts.isPending ? (
        <div>Loading...</div>
      ) : (
        <ArchiveFileForm
          onSubmit={(values: ArchiveFileFormType) => AddArchiveFileAction(values, fetchWithAuth)}
          archiveGroups={archiveGroups.data.data}
          emonHosts={emonHosts.data.data}
        />
      )}
    </div>
  )
}

export default AddArchiveFile

