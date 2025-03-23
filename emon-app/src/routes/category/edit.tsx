import { PromiseFormActionType, CategoryEdit, EditCrudComponentProps } from "@/lib/types";
import { CategoryForm, CategoryFormType } from "./form";
import { useAuth } from "@/hooks/use-auth";
import { useParams } from "react-router";
import { useQuery } from "@tanstack/react-query";

import { validateIds } from "@/lib/utils";
import { Loader } from "@/components/layout/loader";
import { requestCatchError, requestErrorResponse } from "@/helpers/formActions";

const EditCategoryAction = async (
  category_id: number,
  values: CategoryFormType,
  fetchWithAuth: (
    input: RequestInfo,
    init?: RequestInit
  ) => Promise<Response>
): PromiseFormActionType => {

  const data = {
    ...values,
    id: category_id
  }
  const requestTitle = "Edit Category";
  const redirect = `/category`;
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
    return requestErrorResponse(
      response,
      requestTitle,
      redirect
    )
  } catch (error: unknown) {
    return requestCatchError(error, requestTitle)
  }
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