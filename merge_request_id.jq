reduce .[1][] as $item1 ({};
  .[$item1."request_id"] = $item1
) as $dict1
| .[0][]
| if $dict1[."request_id"] then
    . + $dict1[."request_id"]
  else
    .
  end
