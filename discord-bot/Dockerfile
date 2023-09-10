FROM oven/bun

RUN mkdir -p /home/bun/app/node_modules
RUN chown -R bun:bun /home/bun/app/node_modules

WORKDIR /home/bun/app

COPY --chown=bun:bun package.json bun.lockb ./

USER bun

RUN bun install --frozen-lockfile

COPY --chown=bun:bun . .

CMD [ "bun", "start" ]
