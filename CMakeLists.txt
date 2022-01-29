cmake_minimum_required(VERSION 3.10)

project(TP2)

set(_PROTO_FILES central pares)
set(_PROTO_DIR proto)

set(_PROTO_GENERATED_FILES)
foreach(_proto_file ${_PROTO_FILES})
    add_custom_command(
        OUTPUT ${_proto_file}_pb2.py ${_proto_file}_pb2_grpc.py
        DEPENDS ${_PROTO_DIR}/${_proto_file}.proto
        COMMAND python -m grpc_tools.protoc -I ${_PROTO_DIR} --python_out=. --grpc_python_out=. ${_proto_file}.proto
        )
    set(_PROTO_GENERATED_FILES ${_PROTO_GENERATED_FILES} ${_proto_file}_pb2.py ${_proto_file}_pb2_grpc.py)
endforeach()

add_custom_target(proto
    ALL
    DEPENDS ${_PROTO_GENERATED_FILES}
    )

foreach(_target
        cli_pares serv_pares
        cli_central serv_central)
    add_custom_target(
        run_${_target}
        COMMAND ./${_target}.py $(arg)
        DEPENDS ${_PROTO_GENERATED_FILES}
    )
endforeach()

add_custom_target(
    run_serv_pares1
    COMMAND ./serv_pares.py $(arg)
)
add_custom_target(
    run_serv_pares2
    COMMAND ./serv_pares.py $(arg) qqcoisa
)
