import { AddActionType } from "@/lib/types";
import { DataPathForm, DataPathFormType } from "./form";
import { useAuth } from "@/hooks/use-auth";
import { useNavigate, useParams } from "react-router";
import { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";

const EditDataPathAction = async(
  path_id: number,
  values: DataPathFormType,
  fetchWithAuth: (
    input: RequestInfo,
    init?: RequestInit
  ) => Promise<Response>
): AddActionType => {
  
  const data = {
      ...values,
      id: path_id
  }

  try {
    const response = await fetchWithAuth(
      `http://127.0.0.1:8000/api/v1/data_path/edit/${path_id}/`,
      {
        method: 'PUT',
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

  return {success: true, redirect: `/data-path`};
};

function EditDataPath() {
  const { isAuthenticated, fetchWithAuth } = useAuth();
  const { path_id } = useParams();
  const navigate = useNavigate();
  useEffect(() => {
      if (!isAuthenticated) {
        navigate("/login");
      }
    }, [isAuthenticated, navigate]);

  const currentItem = useQuery(
    {
      queryKey: ['data_path', path_id],
      retry: false,
      refetchOnMount: 'always',  // Always refetch when the component mounts
      queryFn: () =>
        fetchWithAuth(
          `http://127.0.0.1:8000/api/v1/data_path/get/${path_id}/`,
          {
            method: 'GET',
          }
        ).then((response) => response.json()),
    }
  );
  return (
    <div>
      {currentItem.isPending ? (
        <div>Loading...</div>
      ) : (
        <>
          {currentItem.isError || !currentItem.data ? (
            <div>No data available: {currentItem.error ? currentItem.error.message : ''}</div>
          ) : (
            <DataPathForm
              onSubmit={(values: DataPathFormType) => EditDataPathAction(
                Number(path_id),
                values,
                fetchWithAuth
              )}
              data={{...currentItem.data.data}}
            />
          )}
        </>
      )}
      
    </div>
  )
}

export default EditDataPath