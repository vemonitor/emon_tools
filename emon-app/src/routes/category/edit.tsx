import { AddActionType, CategoryEdit, EditCrudComponentProps } from "@/lib/types";
import { CategoryForm, CategoryFormType } from "./form";
import { useAuth } from "@/hooks/use-auth";
import { useParams } from "react-router";
import { useQuery } from "@tanstack/react-query";
import { Loader } from "lucide-react";
import { validateIds } from "@/lib/utils";

const EditCategoryAction = async (
  category_id: number,
  values: CategoryFormType,
  fetchWithAuth: (
    input: RequestInfo,
    init?: RequestInit
  ) => Promise<Response>
): AddActionType => {

  const data = {
    ...values,
    id: category_id
  }

  try {
    const response = await fetchWithAuth(
      `/api/v1/category/edit/${category_id}/`,
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

  return { success: true, redirect: `/category` };
};

function EditCategory({
  row_id,
  is_dialog,
  successCallBack,
}: EditCrudComponentProps<CategoryEdit>) {
  const { fetchWithAuth } = useAuth();
  const { category_id } = useParams();
  const item_id = validateIds(category_id, row_id);
  const currentItem = useQuery(
    {
      queryKey: ['category_edit'],
      retry: false,
      refetchOnMount: 'always',  // Always refetch when the component mounts
      queryFn: () =>
        fetchWithAuth(
          `/api/v1/category/get/${item_id}/`,
          {
            method: 'GET',
          }
        ).then((response) => response.json()),
    }
  );
  return (
    <div>
      {currentItem.isPending ? (
        <Loader />
      ) : currentItem.isError || !currentItem.data || !currentItem.data.data ? (
        <div>No data available: {currentItem.error ? currentItem.error.message : ''}</div>
      ) : (
        <CategoryForm
          handleSubmit={(values: CategoryFormType) => EditCategoryAction(
            item_id,
            values,
            fetchWithAuth
          )}
          is_dialog={is_dialog}
          successCallBack={successCallBack}
          data={{ ...currentItem.data.data }}
        />
      )}

    </div>
  )
}

export default EditCategory